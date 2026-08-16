#!/usr/bin/env python3
"""Attach frida to the running Mutagenic process and grab the script key."""
import json
import sys
from pathlib import Path

import frida


def main() -> int:
    pid = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if pid:
        session = frida.attach(pid)
    else:
        session = frida.attach("Mutagenic.exe")
    print(f"attached: {session}")
    script = session.create_script(Path("scripts/frida_grab_key.js").read_text(encoding="utf-8"))

    def on_message(message, data):
        if message["type"] == "send":
            payload = message["payload"]
            if payload.get("type") == "key":
                key = payload["hex"]
                print(f"SCRIPT KEY: {key}")
                Path("manifests/script_key.txt").write_text(key + "\n", encoding="ascii")
                print("saved to manifests/script_key.txt")
            elif payload.get("type") == "error":
                print("JS error:", payload.get("msg"))
        elif message["type"] == "error":
            print("frida error:", message.get("description"))

    script.on("message", on_message)
    script.load()
    print("script loaded; waiting for key (keep game running / trigger script load) ...")
    # stay alive for a while
    import time
    for _ in range(120):
        if Path("manifests/script_key.txt").exists():
            session.detach()
            return 0
        time.sleep(1)
    session.detach()
    return 1


if __name__ == "__main__":
    sys.exit(main())

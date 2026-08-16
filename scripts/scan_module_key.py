#!/usr/bin/env python3
"""Quick scan of the game module memory for hex-string keys (char32/utf16/ascii).

Tests each candidate as AES-256-ECB key against a .gde GDEC MD5.
Usage:
    python scripts/scan_module_key.py <pid> <gde_file> [-o keyfile] [--all]
"""

import hashlib
import re
import sys
from pathlib import Path

import frida
from Crypto.Cipher import AES

ASCII64 = re.compile(rb"[0-9a-fA-F]{32,72}")
UTF16 = re.compile(rb"(?:[0-9a-fA-F]\x00){32,72}")
CHAR32 = re.compile(rb"(?:[0-9a-fA-F]\x00\x00\x00){32,72}")
CHUNK = 8 * 1024 * 1024

JS = r"""
const mod = Process.getModuleByName('Mutagenic.exe');
rpc.exports = {
    base: () => mod.base.toString(),
    size: () => mod.size,
    chunk: (off, size) => {
        try {
            const buf = mod.base.add(off).readByteArray(size);
            return Array.from(new Uint8Array(buf));
        } catch (e) { return []; }
    },
};
"""


def load_gde(path: Path):
    d = path.read_bytes()
    md5d = d[8:24]
    plen = int.from_bytes(d[24:32], "little")
    enc = d[32:]
    return md5d, plen, enc


def main() -> int:
    pid = int(sys.argv[1])
    gde = Path(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    md5d, plen, enc = load_gde(gde)
    session = frida.attach(pid)
    script = session.create_script(JS)
    script.load()
    size = script.exports_sync.size()
    print(f"module size: {size}")

    scanned = 0
    for off in range(0, size, CHUNK):
        data = bytes(script.exports_sync.chunk(off, min(CHUNK, size - off)))
        cands = []
        for pat in (ASCII64, UTF16, CHAR32):
            for mm in pat.finditer(data):
                if pat is ASCII64:
                    cands.append(mm.group().decode("ascii"))
                elif pat is UTF16:
                    cands.append("".join(chr(b) for b in mm.group()[::2]))
                else:
                    cands.append("".join(chr(b) for b in mm.group()[::4]))
        for s in cands:
            s = s.strip()
            if len(s) < 32:
                continue
            variants = [s[:32]]
            if len(s) >= 64:
                variants += [s[32:64], s[:64]]
            for part in variants:
                if len(part) == 64:
                    try:
                        keys = [bytes.fromhex(part)]
                    except ValueError:
                        keys = []
                else:
                    keys = [part.encode("ascii")]
                for key in keys:
                    plain = AES.new(key, AES.MODE_ECB).decrypt(enc)[:plen]
                    if hashlib.md5(plain).digest() == md5d:
                        print(f"KEY FOUND at module+0x{off:x}: {s}")
                        print(f"  key: {key.hex()}")
                        if out:
                            out.write_text(key.hex() + "\n", encoding="ascii")
                        session.detach()
                        return 0
        scanned += len(data)
    print(f"module scanned {scanned} bytes, no key")
    session.detach()
    return 1


if __name__ == "__main__":
    sys.exit(main())

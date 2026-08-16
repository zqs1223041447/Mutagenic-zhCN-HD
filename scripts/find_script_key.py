#!/usr/bin/env python3
"""Find the AES key for Godot .gde scripts by brute-forcing hex-string
candidates found in the EXE, verifying against the GDEC header MD5.

Key derivation (Godot 3.5, modules/gdscript/gdscript.cpp):
    Vector<uint8_t> key; key.resize(32);
    for i in 32: key[i] = script_encryption_key[i]   # ASCII of first 32 chars
Format (core/io/file_access_encrypted.cpp):
    "GDEC"(4) mode=1(4) md5_of_plaintext(16) plaintext_len(8) AES-256-ECB(data)

Usage:
    python scripts/find_script_key.py <exe> <gde_file> [-o <keyfile>]
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

from Crypto.Cipher import AES

HEX64_RE = re.compile(rb"[0-9a-fA-F]{64}")
HEX32_RE = re.compile(rb"[0-9a-fA-F]{32}")


def load_gde(path: Path):
    d = path.read_bytes()
    assert d[:4] == b"GDEC", "not a GDEC script"
    mode = int.from_bytes(d[4:8], "little")
    md5d = d[8:24]
    plen = int.from_bytes(d[24:32], "little")
    enc = d[32:]
    return mode, md5d, plen, enc


def try_key(key_bytes: bytes, md5d: bytes, enc: bytes, plen: int):
    if len(key_bytes) != 32:
        return None
    if len(enc) % 16:
        return None
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    try:
        plain = cipher.decrypt(enc)[:plen]
    except ValueError:
        return None
    if hashlib.md5(plain).digest() == md5d:
        return plain
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Brute-force Godot .gde script key")
    ap.add_argument("exe", type=Path)
    ap.add_argument("gde", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None)
    args = ap.parse_args()

    mode, md5d, plen, enc = load_gde(args.gde)
    print(f"gde {args.gde}: mode={mode} plaintext_len={plen} "
          f"enc_len={len(enc)} md5={md5d.hex()}")

    exe = args.exe.read_bytes()
    candidates = set()
    for m in HEX64_RE.finditer(exe):
        s = m.group().decode("ascii")
        candidates.add(s[:32])           # key = first 32 chars of 64-hex
    for m in HEX32_RE.finditer(exe):
        candidates.add(m.group().decode("ascii"))

    print(f"testing {len(candidates)} unique 32-hex candidates...")
    for s in candidates:
        key = s.encode("ascii")
        plain = try_key(key, md5d, enc, plen)
        if plain is not None:
            print(f"KEY FOUND: {s}")
            if args.output:
                args.output.write_text(s + "\n", encoding="ascii")
                print(f"saved: {args.output}")
            # quick peek: is it GDScript bytecode (GDCC) or text?
            print("plaintext head:", plain[:64])
            return 0
    print("no candidate matched")
    return 1


if __name__ == "__main__":
    sys.exit(main())

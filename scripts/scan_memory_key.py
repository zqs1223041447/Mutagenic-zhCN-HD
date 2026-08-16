#!/usr/bin/env python3
"""Scan the running game's process memory for the script encryption key.

Streams readable memory ranges via frida RPC in chunks and tests hex-string
candidates (ASCII / UTF-16 / char32 forms) as AES-256-ECB keys against a
.gde GDEC header MD5.

Usage:
    python scripts/scan_memory_key.py <pid> <gde_file> [-o keyfile]
"""

import hashlib
import re
import sys
from pathlib import Path

import frida
from Crypto.Cipher import AES

ASCII64 = re.compile(rb"[0-9a-fA-F]{40,72}")
UTF16 = re.compile(rb"(?:[0-9a-fA-F]\x00){40,72}")
CHAR32 = re.compile(rb"(?:[0-9a-fA-F]\x00\x00\x00){40,72}")
CHUNK = 16 * 1024 * 1024
MAX_RANGE = 512 * 1024 * 1024

JS = r"""
const ranges = Process.enumerateRanges('r--');
rpc.exports = {
    count: () => ranges.length,
    size: (i) => ranges[i].size,
    base: (i) => ranges[i].base.toString(),
    chunk: (i, off, size) => {
        const r = ranges[i];
        try {
            const buf = r.base.add(off).readByteArray(size);
            return Array.from(new Uint8Array(buf));
        } catch (e) {
            return [];
        }
    },
};
"""


def load_gde(path: Path):
    d = path.read_bytes()
    assert d[:4] == b"GDEC"
    md5d = d[8:24]
    plen = int.from_bytes(d[24:32], "little")
    enc = d[32:]
    return md5d, plen, enc


def main() -> int:
    pid = int(sys.argv[1])
    gde = Path(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    md5d, plen, enc = load_gde(gde)
    print(f"target: md5={md5d.hex()} plen={plen}")

    session = frida.attach(pid)
    script = session.create_script(JS)
    script.load()
    n = script.exports_sync.count()
    print(f"readable ranges: {n}")

    scanned = 0
    for i in range(n):
        size = script.exports_sync.size(i)
        if size > MAX_RANGE or size <= 0:
            continue
        base = script.exports_sync.base(i)
        off = 0
        while off < size:
            ln = min(CHUNK, size - off)
            try:
                data = bytes(script.exports_sync.chunk(i, off, ln))
            except frida.InvalidOperationError:
                # script died; re-create it and continue
                session.detach()
                session = frida.attach(pid)
                script = session.create_script(JS)
                script.load()
                continue
            if not data:
                break
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
                for part in (s[:32], s[32:64] if len(s) >= 64 else ""):
                    if len(part) != 32:
                        continue
                    key = part.encode("ascii")
                    plain = AES.new(key, AES.MODE_ECB).decrypt(enc)[:plen]
                    if hashlib.md5(plain).digest() == md5d:
                        print(f"KEY FOUND at {base}+0x{off:x}: {part}")
                        if out:
                            out.write_text(part + "\n", encoding="ascii")
                            print(f"saved: {out}")
                        session.detach()
                        return 0
            scanned += ln
            off += ln
            if scanned % (256 * 1024 * 1024) < ln:
                print(f"scanned {scanned // (1024*1024)} MB ...")
    print(f"scanned total {scanned // (1024*1024)} MB, no key found")
    session.detach()
    return 1


if __name__ == "__main__":
    sys.exit(main())

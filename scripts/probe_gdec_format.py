"""Verify the GDEC (.gde) container layout against an original file.

Layout (Godot 3.x FileAccessEncrypted):
    0..4    "GDEC" magic
    4..8    u32 mode  (MODE_WRITE_AES256 == 1)
    8..24   md5(plaintext)            16 bytes
    24..32  u64 plaintext length
    32..    AES-256-ECB ciphertext, padded to a 16-byte boundary

Confirms whether GDRE's --compile output is the exact plaintext by comparing
both the stored md5 and the stored length.
"""
import hashlib
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GDRE = ROOT / "02_tools/gdre/gdre_tools.exe"
PROBE = ROOT / "10_logs/gdec_probe"
REL = "Globals/Colors"


def parse_gdec(raw: bytes) -> dict:
    return {
        "magic": raw[0:4],
        "mode": struct.unpack_from("<I", raw, 4)[0],
        "md5": raw[8:24],
        "length": struct.unpack_from("<Q", raw, 24)[0],
        "cipher_len": len(raw) - 32,
    }


def main() -> int:
    gde = (ROOT / "03_raw" / f"{REL}.gde").read_bytes()
    h = parse_gdec(gde)
    print(f"=== original {REL}.gde ({len(gde)} bytes) ===")
    print(f"  magic       : {h['magic']!r}")
    print(f"  mode        : {h['mode']}   (1 == MODE_WRITE_AES256)")
    print(f"  md5         : {h['md5'].hex()}")
    print(f"  length      : {h['length']}")
    print(f"  cipher_len  : {h['cipher_len']}  (16-aligned: "
          f"{h['cipher_len'] % 16 == 0})")

    PROBE.mkdir(parents=True, exist_ok=True)
    out = PROBE / f"{Path(REL).name}.gdc"
    if out.exists():
        out.unlink()
    subprocess.run(
        [str(GDRE), "--headless",
         f"--compile={ROOT / '06_worktree' / (REL + '.gd')}",
         "--bytecode=3.5.3.stable", f"--output={PROBE}"],
        capture_output=True, text=True,
    )
    if not out.exists():
        print("compile FAILED")
        return 1

    gdc = out.read_bytes()
    md5 = hashlib.md5(gdc).digest()
    pad = (16 - len(gdc) % 16) % 16
    print(f"\n=== our compiled {REL}.gdc ({len(gdc)} bytes) ===")
    print(f"  md5         : {md5.hex()}")
    print(f"  padded size : {len(gdc) + pad}")

    ok_len = h["length"] == len(gdc)
    ok_md5 = h["md5"] == md5
    ok_pad = h["cipher_len"] == len(gdc) + pad
    print("\n=== comparison ===")
    print(f"  length match      : {ok_len}")
    print(f"  md5 match         : {ok_md5}")
    print(f"  cipher size match : {ok_pad}")
    verdict = ("BYTECODE IDENTICAL - only AES step missing"
               if (ok_len and ok_md5 and ok_pad) else "MISMATCH")
    print(f"  VERDICT           : {verdict}")
    return 0 if (ok_len and ok_md5 and ok_pad) else 1


if __name__ == "__main__":
    sys.exit(main())

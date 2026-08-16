import struct

def check_pck_tail(path, label):
    with open(path, 'rb') as f:
        f.seek(0, 2)
        size = f.tell()
        print(f"\n{label}")
        print(f"  file size: {size}")
        f.seek(-4, 2)
        magic = f.read(4)
        print(f"  last 4 bytes: {magic} ({magic.hex()})")
        f.seek(-12, 2)
        last12 = f.read(12)
        print(f"  last 12 bytes: {' '.join(f'{b:02x}' for b in last12)}")
        val64 = struct.unpack_from('<Q', last12, 0)[0]
        val32 = struct.unpack_from('<I', last12, 8)[0]
        print(f"  interpreted [u64={val64}] [u32=0x{val32:08X}]")
        if magic == b'GDPC':
            print(f"  -> ends with GDPC magic OK")
            # The u64 should be the PCK start offset
            print(f"  -> pck_start from tail: {val64}  (expected 40545280 = 0x{40545280:X})")
        else:
            print(f"  -> does NOT end with GDPC!")

check_pck_tail("00_original/Mutagenic.exe", "ORIGINAL")
check_pck_tail("09_output/Mutagenic.exe",   "OUR BUILD")

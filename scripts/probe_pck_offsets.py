"""Decode first few entries from a PCK (embedded or standalone) and
inspect the bytes at the stored offset to guess the offset convention."""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PCK_OFFSET = 40545280  # EXE offset where PCK lives

def read_u32(data, pos):  return struct.unpack_from('<I', data, pos)[0]
def read_u64(data, pos):  return struct.unpack_from('<Q', data, pos)[0]

def decode_entries(label, path, pck_base_in_file=0, n=3):
    """Read n file entries from a PCK at pck_base_in_file inside `path`."""
    with open(path, 'rb') as f:
        f.seek(pck_base_in_file)
        raw_header = f.read(88 + 3000)   # header + room for a few entries

    magic      = raw_header[0:4]
    file_count = read_u32(raw_header, 84)
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"  magic={magic}, file_count={file_count}, pck_base_in_file={pck_base_in_file}")

    pos = 88
    for i in range(min(n, file_count)):
        path_len = read_u32(raw_header, pos);  pos += 4
        # Godot PCK: string is path_len bytes long (null-terminated + padded to 4)
        p = raw_header[pos:pos+path_len].decode('utf-8', errors='replace').rstrip('\x00')
        pos += path_len
        offset = read_u64(raw_header, pos);  pos += 8
        size   = read_u64(raw_header, pos);  pos += 8
        md5    = raw_header[pos:pos+16].hex();  pos += 16

        # Probe data at two interpretations:
        #   A) absolute  : offset is already the absolute position in the file
        #   B) pck-rel   : offset is relative to PCK start → absolute = pck_base + offset
        with open(path, 'rb') as f:
            abs_a = offset
            abs_b = pck_base_in_file + offset
            f.seek(abs_a);  bytes_a = f.read(4)
            f.seek(abs_b);  bytes_b = f.read(4)

        print(f"  [{i}] {p!r}")
        print(f"       stored_offset={offset}  size={size}")
        print(f"       [A] absolute  pos={abs_a}: {bytes_a.hex()}")
        print(f"       [B] pck-rel   pos={abs_b}: {bytes_b.hex()}")

# --- Original embedded PCK ---
decode_entries("ORIGINAL (embedded in EXE)", ROOT/"00_original/Mutagenic.exe",
               pck_base_in_file=PCK_OFFSET, n=3)

# --- GDRE-built embedded PCK ---
decode_entries("OUR BUILD (embedded in EXE)", ROOT/"09_output/Mutagenic.exe",
               pck_base_in_file=PCK_OFFSET, n=3)

#!/usr/bin/env python3
"""修正 PE header 中的 pck section 大小"""
import struct
import sys
from pathlib import Path

EXE_PATH = Path("09_output/Mutagenic.exe")
PCK_SECTION_INDEX = 5  # pck 是第 6 个 section (0-indexed)
PCK_OFFSET = 40545280
NEW_PCK_SIZE = 64410372

def main():
    if not EXE_PATH.exists():
        print(f"Error: {EXE_PATH} not found")
        sys.exit(1)
    
    with open(EXE_PATH, "r+b") as f:
        # 读取 PE header offset (at 0x3C)
        f.seek(0x3C)
        pe_offset = struct.unpack("<I", f.read(4))[0]
        print(f"PE header at: 0x{pe_offset:X}")
        
        # 验证 PE signature
        f.seek(pe_offset)
        sig = f.read(4)
        if sig != b'PE\x00\x00':
            print(f"Error: Invalid PE signature: {sig}")
            sys.exit(1)
        
        # COFF header: 20 bytes
        # Optional header size
        f.seek(pe_offset + 4 + 16)
        opt_hdr_size = struct.unpack("<H", f.read(2))[0]
        print(f"Optional header size: {opt_hdr_size}")
        
        # Number of sections
        f.seek(pe_offset + 4 + 2)
        num_sections = struct.unpack("<H", f.read(2))[0]
        print(f"Number of sections: {num_sections}")
        
        # Section table starts after: PE sig(4) + COFF(20) + Optional(opt_hdr_size)
        section_table_offset = pe_offset + 4 + 20 + opt_hdr_size
        
        # Each section header is 40 bytes
        pck_section_offset = section_table_offset + (PCK_SECTION_INDEX * 40)
        print(f"\nPCK section header at: 0x{pck_section_offset:X}")
        
        # Read current section
        f.seek(pck_section_offset)
        section_data = bytearray(f.read(40))
        
        # Parse section name (8 bytes, null-padded)
        name = section_data[0:8].rstrip(b'\x00').decode('ascii')
        print(f"Section name: {name}")
        
        if name != "pck":
            print(f"Error: Expected 'pck', got '{name}'")
            sys.exit(1)
        
        # Parse current values
        virtual_size = struct.unpack("<I", section_data[8:12])[0]
        virtual_addr = struct.unpack("<I", section_data[12:16])[0]
        raw_size = struct.unpack("<I", section_data[16:20])[0]
        raw_ptr = struct.unpack("<I", section_data[20:24])[0]
        
        print(f"\nCurrent values:")
        print(f"  VirtualSize:      {virtual_size}")
        print(f"  VirtualAddress:   0x{virtual_addr:X}")
        print(f"  SizeOfRawData:    {raw_size}")
        print(f"  PointerToRawData: 0x{raw_ptr:X}")
        
        # Update raw size to match new PCK
        new_raw_size = NEW_PCK_SIZE
        
        print(f"\nUpdating SizeOfRawData: {raw_size} -> {new_raw_size}")
        
        # Write new value
        struct.pack_into("<I", section_data, 16, new_raw_size)
        
        # Write back to file
        f.seek(pck_section_offset)
        f.write(section_data)
        
        print("\n✓ PE header updated successfully")
        
        # Verify
        f.seek(pck_section_offset + 16)
        verify = struct.unpack("<I", f.read(4))[0]
        print(f"Verified SizeOfRawData: {verify}")
        
        if verify == new_raw_size:
            print("✓ Verification passed")
        else:
            print("✗ Verification failed!")
            sys.exit(1)

if __name__ == "__main__":
    main()

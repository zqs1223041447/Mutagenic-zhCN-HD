#!/usr/bin/env python3
"""手动嵌入 PCK 到 EXE"""
import argparse
import pathlib
import struct
import sys

# 默认值（可被命令行参数覆盖）
DEFAULT_ORIGINAL_EXE = pathlib.Path("00_original/Mutagenic.exe")
DEFAULT_NEW_PCK = pathlib.Path("09_output/data.pck")
DEFAULT_OUTPUT_EXE = pathlib.Path("09_output/Mutagenic.exe")
PCK_OFFSET = 40545280  # 从 baseline.json 的 pe.sections[pck].raw_ptr

def adjust_pck_entry_offsets(pck_data: bytes, add_offset: int) -> bytes:
    """Convert PCK-relative file offsets to absolute EXE offsets.

    Godot 3.x embedded PCK reader uses stored offsets as absolute positions
    in the EXE file (no addition of PCK base).  GDRE's --pck-create writes
    offsets relative to the PCK start (correct for standalone use).
    When embedding, we must add PCK_start to every entry offset so Godot
    finds the right bytes.
    """
    data = bytearray(pck_data)
    assert data[0:4] == b'GDPC', "Not a valid GDPC PCK"
    file_count = struct.unpack_from('<I', data, 84)[0]
    pos = 88
    for _ in range(file_count):
        path_len = struct.unpack_from('<I', data, pos)[0]
        pos += 4 + path_len          # skip length + path string
        old = struct.unpack_from('<Q', data, pos)[0]
        struct.pack_into('<Q', data, pos, old + add_offset)
        pos += 8 + 8 + 16            # offset + size + md5
    print(f"  Adjusted {file_count} entry offsets (+{add_offset})")
    return bytes(data)


def update_pck_section_size(exe_data, new_pck_size):
    """更新 PE section table 中 pck section 的 raw_size"""
    # Parse PE header
    pe_offset = struct.unpack_from("<I", exe_data, 0x3C)[0]
    coff_offset = pe_offset + 4
    
    # Parse COFF header
    machine, n_sections, timestamp, sym_ptr, sym_count, opt_size, chars = struct.unpack_from(
        "<HHIIIHH", exe_data, coff_offset
    )
    
    # Section table starts after COFF (20 bytes) + optional header
    sections_offset = coff_offset + 20 + opt_size
    
    # Find pck section
    for i in range(n_sections):
        sec_offset = sections_offset + i * 40
        name = exe_data[sec_offset:sec_offset+8].rstrip(b'\x00').decode('ascii', errors='ignore')
        
        if name == 'pck':
            # Update raw_size at offset +16 in section entry
            raw_size_offset = sec_offset + 16
            print(f"  Updating pck section raw_size at offset {raw_size_offset} (0x{raw_size_offset:X})")
            print(f"    Old size: {struct.unpack_from('<I', exe_data, raw_size_offset)[0]}")
            print(f"    New size: {new_pck_size}")
            
            # Create mutable bytearray
            exe_array = bytearray(exe_data)
            struct.pack_into("<I", exe_array, raw_size_offset, new_pck_size)
            return bytes(exe_array)
    
    print("  Warning: pck section not found in PE header")
    return exe_data

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Embed PCK into EXE")
    parser.add_argument("original_exe", nargs="?", type=pathlib.Path, 
                       default=DEFAULT_ORIGINAL_EXE, help="Original EXE file")
    parser.add_argument("pck_file", nargs="?", type=pathlib.Path,
                       default=DEFAULT_NEW_PCK, help="PCK file to embed")
    parser.add_argument("-o", "--output", type=pathlib.Path,
                       default=DEFAULT_OUTPUT_EXE, help="Output EXE file")
    args = parser.parse_args()
    
    ORIGINAL_EXE = args.original_exe
    NEW_PCK = args.pck_file
    OUTPUT_EXE = args.output
    
    if not ORIGINAL_EXE.exists():
        print(f"Error: {ORIGINAL_EXE} not found")
        sys.exit(1)
    
    if not NEW_PCK.exists():
        print(f"Error: {NEW_PCK} not found")
        sys.exit(1)
    
    # 读取原版 EXE（只取 PCK 之前的部分）
    print(f"Reading original EXE up to offset {PCK_OFFSET} (0x{PCK_OFFSET:X})...")
    with open(ORIGINAL_EXE, 'rb') as f:
        exe_header = f.read(PCK_OFFSET)
    
    print(f"  EXE header: {len(exe_header)} bytes")
    
    # 读取新 PCK
    print(f"Reading new PCK from {NEW_PCK}...")
    with open(NEW_PCK, 'rb') as f:
        pck_data = f.read()
    
    print(f"  PCK data: {len(pck_data)} bytes")
    
    # 验证 PCK magic
    if pck_data[:4] != b'GDPC':
        print("Error: PCK file does not start with GDPC magic")
        sys.exit(1)
    
    # 验证 PCK 尾部结构（Godot 嵌入检测依赖它）
    if pck_data[-4:] != b'GDPC':
        print("Error: PCK does not END with GDPC magic; not embeddable")
        sys.exit(1)

    # 将 PCK 内 file entry 偏移从「PCK 相对」转为「EXE 绝对」
    # Godot 3.x 嵌入 PCK 读取器直接把存储偏移当 EXE 绝对地址使用（不加 PCK base）。
    # GDRE --pck-create 输出的是 PCK 相对偏移（standalone 用法），嵌入前必须加上 PCK_OFFSET。
    print(f"Adjusting PCK entry offsets to absolute EXE positions (+{PCK_OFFSET})...")
    pck_data = adjust_pck_entry_offsets(pck_data, PCK_OFFSET)

    # 更新 PE section table 中的 pck section 大小
    print(f"Updating PE section table...")
    exe_header = update_pck_section_size(exe_header, len(pck_data))

    # 修正 PCK 尾部偏移字段
    #
    # Godot 3.x 定位嵌入式 PCK 的算法（自文件末尾反向读取）：
    #   1. 读末尾 4 字节 -> 必须是 GDPC
    #   2. 读其前 8 字节 -> u64 ds
    #   3. PCK 起点 = file_size - ds - 12，并在该处再次校验 GDPC
    #
    # 因此 ds 必须等于 (PCK 字节数 - 12)。GDRE 生成的 standalone PCK
    # 把该字段留为 0，直接嵌入会让 Godot 在错误位置寻找 PCK，
    # 表现为启动时弹出 "Couldn't load project data at path"。
    pck_array = bytearray(pck_data)
    tail_value = len(pck_data) - 12
    old_tail = struct.unpack_from("<Q", pck_array, len(pck_array) - 12)[0]
    struct.pack_into("<Q", pck_array, len(pck_array) - 12, tail_value)
    print(f"Patching PCK tail offset field:")
    print(f"    Old ds: {old_tail}")
    print(f"    New ds: {tail_value}  (= pck_size - 12)")
    pck_data = bytes(pck_array)

    # 合并并写入
    print(f"Writing combined EXE to {OUTPUT_EXE}...")
    OUTPUT_EXE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_EXE, 'wb') as f:
        f.write(exe_header)
        f.write(pck_data)
    
    final_size = len(exe_header) + len(pck_data)
    print(f"✓ Done: {final_size} bytes")
    
    # 验证
    print("\nVerification:")
    with open(OUTPUT_EXE, 'rb') as f:
        # 检查 PE header
        f.seek(0)
        if f.read(2) != b'MZ':
            print("  ✗ Missing PE header (MZ)")
            sys.exit(1)
        print("  ✓ PE header (MZ) present")
        
        # 检查 PCK magic
        f.seek(PCK_OFFSET)
        if f.read(4) != b'GDPC':
            print(f"  ✗ Missing PCK magic at offset {PCK_OFFSET}")
            sys.exit(1)
        print(f"  ✓ PCK magic (GDPC) at offset {PCK_OFFSET}")
        
        # 检查文件末尾
        f.seek(-4, 2)
        end_bytes = f.read(4)
        print(f"  File ends with: {end_bytes.hex()}")
    
    print("\n✓ EXE with embedded PCK created successfully")

if __name__ == "__main__":
    main()

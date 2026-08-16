#!/usr/bin/env python3
"""批量编译 06_worktree 中的 .gd 为 .gdc"""
import pathlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

GDRE = pathlib.Path("02_tools/gdre/gdre_tools.exe")
BYTECODE = "3.5.0-stable"
WORKTREE = pathlib.Path("06_worktree")
OUTPUT = pathlib.Path("07_compiled")

def compile_file(gd_file: pathlib.Path) -> tuple[pathlib.Path, bool, str]:
    """编译单个 .gd 文件"""
    rel_path = gd_file.relative_to(WORKTREE)
    out_file = OUTPUT / rel_path.with_suffix(".gdc")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        result = subprocess.run(
            [str(GDRE), "--headless", f"--bytecode={BYTECODE}", 
             f"--compile={gd_file}", f"--output={out_file}"],
            capture_output=True, text=True, timeout=30
        )
        success = result.returncode == 0 and out_file.exists()
        msg = result.stderr if result.stderr else result.stdout
        return (rel_path, success, msg.strip())
    except Exception as e:
        return (rel_path, False, str(e))

def main():
    if not GDRE.exists():
        print(f"Error: gdre not found at {GDRE}")
        sys.exit(1)
    
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    # 收集所有 .gd 文件
    gd_files = list(WORKTREE.rglob("*.gd"))
    print(f"Found {len(gd_files)} .gd files in {WORKTREE}")
    
    if not gd_files:
        print("No .gd files found")
        return
    
    # 并行编译（限制并发数避免资源耗尽）
    success_count = 0
    fail_count = 0
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(compile_file, f): f for f in gd_files}
        
        for i, future in enumerate(as_completed(futures), 1):
            rel_path, success, msg = future.result()
            
            if success:
                success_count += 1
                print(f"[{i}/{len(gd_files)}] ✓ {rel_path}")
            else:
                fail_count += 1
                print(f"[{i}/{len(gd_files)}] ✗ {rel_path}")
                if msg and "Error" in msg:
                    print(f"  {msg[:200]}")
    
    print(f"\n{'='*60}")
    print(f"Compilation complete: {success_count} OK, {fail_count} failed")
    print(f"Output: {OUTPUT.resolve()}")
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()

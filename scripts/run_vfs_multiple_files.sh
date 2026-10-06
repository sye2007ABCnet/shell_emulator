#!/bin/bash
# Загрузка VFS с некоторыми файлами на одном уровне.
cd "$(dirname "$0")/.."
printf "ls\nexit\n" | python3 src/emulator.py --vfs-path fixtures/vfs/multiple_files.json
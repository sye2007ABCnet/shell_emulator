#!/bin/bash
# Запуск с --vfs-path и --prompt: проверяем, что имя VFS берётся из пути,
# а приглашение - пользовательское.
cd "$(dirname "$0")/../src"
printf "ls\nexit\n" | python3 emulator.py \
  --vfs-path /tmp/myshell_vfs.json \
  --prompt "myshell:~$ "

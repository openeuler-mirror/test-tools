#!/bin/bash

echo "========== 系统诊断检查 =========="
echo ""

echo "1. 系统负载和运行时间:"
uptime
echo ""

echo "2. 核心转储文件:"
ls -la /var/lib/systemd/coredump/
echo ""

echo "3. 内存使用情况 (GB):"
free -g
echo ""

echo "4. 详细内存信息:"
cat /proc/meminfo | grep -E "^(MemTotal|MemFree|MemAvailable|Buffers|Cached|SwapTotal|SwapFree|Dirty|Writeback|Slab)"
echo ""

echo "5. Slab缓存使用 (排序):"
cat /proc/slabinfo | awk '{print $3*$4/1024,"KB",$1}' | sort -nr -k 1 | head -20
echo ""

echo "6. 进程内存使用排行:"
ps aux --sort=-rss | head -10 | awk '{printf "%-10s %-10s %-10s %-s\n", $1, $2, $6/1024"MB", $11}'
echo ""

echo "7. 大文件检查:"
echo "/var/log 下的大文件:"
find /var/log -type f -size +10M -exec ls -lh {} \; 2>/dev/null
echo ""
echo "/home 下的大文件:"
find /home -type f -size +10M -exec ls -lh {} \; 2>/dev/null
echo ""

echo "8. 网络统计:"
echo "Netlink套接字数: $(cat /proc/net/netlink | wc -l)"
echo ""

echo "9. 异常进程检查:"
echo "D状态进程:"
ps -A -o stat,ppid,pid,cmd | grep -e '^[Dd]'
echo ""
echo "僵尸进程:"
ps -A -o stat,ppid,pid,cmd | grep -e '^[Zz]'
echo ""

echo "10. 已删除但打开的文件:"
ls -l /proc/*/fd/* 2>/dev/null | grep delete | head -10
echo ""

echo "11. 系统资源限制:"
ulimit -a
echo ""

echo "12. 核心转储配置:"
echo "Core pattern: $(cat /proc/sys/kernel/core_pattern)"
core_dir=$(dirname $(cat /proc/sys/kernel/core_pattern | awk '{print $1}' | awk -F "|" '{print $NF}'))
echo "Core目录: $core_dir"
if [ -d "$core_dir" ]; then
    ls -la "$core_dir" | head -10
else
    echo "目录不存在: $core_dir"
fi


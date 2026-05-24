#!/bin/bash
# PCL2 主页自动更新脚本
# 功能：拉取最新数据 → 生成 Custom.xaml → 同步到 Windows → 同步到服务器
# 由 cron 每3天触发一次

set -e

PCL2_DIR="/home/ftc13/pcl2"
OUTPUT_DIR="$PCL2_DIR/output"
WIN_DIR="/mnt/d/pcl/PCL"
SSH_KEY="$HOME/.ssh/id_ecs"
SERVER="root@139.196.113.49"
SERVER_PATH="/var/www/pcl2-homepage/output/"
LOG_FILE="$PCL2_DIR/auto_update.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "=== PCL2 主页自动更新开始 ==="

# 1. 使用 Claude Code 生成更新的 Custom.xaml
# cc/claude 会读取当前数据，生成新的 XAML，更新 version，计算 CRC
log "生成 Custom.xaml..."

cd "$PCL2_DIR"

# 使用 claude --print 生成更新内容
claude --print "你是一个 PCL2 Custom.xaml 生成器。

任务：读取 $PCL2_DIR/output/Custom.xaml 文件，更新其中的整合包推荐和视频推荐部分。

【整合包推荐】三条规则：
1. 删除重复项（同一个整合包出现多次的，只保留一个）
2. 从 modpacks_data.json（同目录）读取数据，按播放量/下载量排序，替换掉旧的条目
3. 保持 3 列布局，每列约 10 个条目

【视频推荐】三条规则：
1. 保留 UP 主频道推荐不变
2. 热门视频区域换成最新几天播放量最高的 B站视频
3. 保持 3 列布局

【其他】
- 更新顶部的注释时间戳为当天
- 更新 output/version.txt 为 v1.0.$(date +%m%d)
- 计算新的 CRC32 写入 Custom.xaml.ini，格式为 \$(date +%d%H%M):\$(crc32)
- 不要改动关于区块和样式

生成新文件后输出到 $OUTPUT_DIR/Custom.xaml，同时更新 version.txt 和 Custom.xaml.ini。" 2>&1 >> "$LOG_FILE"

log "Custom.xaml 生成完成"

# 2. 计算 CRC 并更新 ini（备用，如果 claude 没做的话）
python3 -c "
import zlib
with open('$OUTPUT_DIR/Custom.xaml', 'rb') as f:
    data = f.read()
crc = zlib.crc32(data) & 0xFFFFFFFF
ts = '$(date +%d%H%M)'
with open('$OUTPUT_DIR/Custom.xaml.ini', 'w') as f:
    f.write(f'{ts}:{crc:08x}')
print(f'CRC updated: {ts}:{crc:08x}')
" >> "$LOG_FILE" 2>&1

log "CRC 更新完成"

# 3. 同步到 Windows
if [ -d "$WIN_DIR" ]; then
    cp "$OUTPUT_DIR/Custom.xaml" "$WIN_DIR/Custom.xaml"
    cp "$OUTPUT_DIR/Custom.xaml.ini" "$WIN_DIR/Custom.xaml.ini"
    cp "$OUTPUT_DIR/version.txt" "$WIN_DIR/version.txt"
    log "Windows 同步完成"
else
    log "WARNING: Windows 目录 $WIN_DIR 不存在，跳过"
fi

# 4. 同步到服务器
if [ -f "$SSH_KEY" ]; then
    scp -i "$SSH_KEY" "$OUTPUT_DIR/Custom.xaml" "$SERVER:$SERVER_PATH" 2>&1 >> "$LOG_FILE"
    scp -i "$SSH_KEY" "$OUTPUT_DIR/Custom.xaml.ini" "$SERVER:$SERVER_PATH" 2>&1 >> "$LOG_FILE"
    scp -i "$SSH_KEY" "$OUTPUT_DIR/version.txt" "$SERVER:$SERVER_PATH" 2>&1 >> "$LOG_FILE"
    log "服务器同步完成"
else
    log "WARNING: SSH 密钥 $SSH_KEY 不存在，跳过服务器同步"
fi

log "=== PCL2 主页自动更新结束 ==="

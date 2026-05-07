#!/bin/bash
# PCL2 主页同步到 spark-4643 服务器
set -e

HOST="nlhdst@100.118.0.63"
DEST="/var/www/pcl2-homepage"

echo "📤 同步到 spark-4643..."

scp output/Custom.xaml "$HOST:$DEST/"
scp output/Custom.xaml.ini "$HOST:$DEST/"
scp output/version.txt "$HOST:$DEST/"

# 如果有图标目录，也同步
if [ -d "icons" ]; then
    rsync -avz --delete icons/ "$HOST:$DEST/icons/" 2>/dev/null || true
fi

echo "✅ 同步完成 — PCL2 刷新即可"

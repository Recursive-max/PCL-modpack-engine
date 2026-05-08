#!/bin/bash
# PCL2 主页同步到阿里云 ECS
# PCL2 域名: qawsedrftgyhujiko.fun (Cloudflare proxy)
set -e

HOST="ecs"
DEST="/var/www/pcl2-homepage"
TMP="/tmp/pcl2-sync-$$"

echo "📤 同步到阿里云 ECS..."

# 同步主文件（cat + sudo tee 绕过 scp 权限问题）
cat output/Custom.xaml | ssh "$HOST" "sudo tee $DEST/Custom.xaml > /dev/null"
cat output/Custom.xaml.ini | ssh "$HOST" "sudo tee $DEST/Custom.xaml.ini > /dev/null"
cat output/version.txt | ssh "$HOST" "sudo tee $DEST/version.txt > /dev/null"

# 同步图标
if [ -d "icons" ]; then
  ssh "$HOST" "mkdir -p $DEST/icons"
  tar czf - -C icons . | ssh "$HOST" "sudo tar xzf - -C $DEST/icons"
fi

# 修正权限
ssh "$HOST" "sudo chown -R www-data:www-data $DEST" 2>/dev/null || true

echo "✅ 同步完成 — PCL2 刷新即可 (ECS 本地 serve)"

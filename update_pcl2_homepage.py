#!/usr/bin/env python3
"""
PCL2 主页自动更新脚本
功能: 读取数据 → 生成 XAML → 同步 Windows → 同步服务器
运行方式: cron (每3天) 或手动
"""
import json, re, zlib, shutil, os, sys
from datetime import datetime

BASE = os.path.expanduser("~/pcl2")
OUTPUT = os.path.join(BASE, "output")
WIN = os.path.join("/mnt/d/pcl/PCL")
SSH_KEY = os.path.expanduser("~/.ssh/id_ecs")
SERVER = "root@139.196.113.49"
SERVER_PATH = "/var/www/pcl2-homepage/output/"
LOG_FILE = os.path.join(BASE, "auto_update.log")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# ===== 图标分类系统 =====
CATEGORY_MAP = [
    # (关键词列表, 图标, 分类名)
    (["宝可梦", "神奇宝贝", "pixelmon", "cobblemon", "方可梦", "pokemon", "pokemon", "cobbleverse"], "Egg.png", "宝可梦"),
    (["fabulously", "optimized", "sodium", "optifabric", "fps", "vanilla perfected", "remarkably"], "Fabric.png", "优化"),
    (["红石", "科技", "create", "机械动力", "格雷", "stoneblock", "all the mods", "ftb", "craftoria"], "RedstoneBlock.png", "科技"),
    (["恐怖", "rlcraft", "dread", "zombie", "horror", "deceased", "backrooms", "cursed walking", "nightfall", "cave horror"], "CommandBlock.png", "硬核"),
    (["冒险", "rpg", "勇者之章", "龙之冒险", "prehistoric", "dawncraft", "双人德爷", "cisco", "beyond depth", "better mc"], "Anvil.png", "冒险"),
    (["魔法", "愚者", "奇幻", "咒次元", "prominence", "森罗万藏"], "RedstoneLampOn.png", "魔法"),
    (["乌托邦", "中世纪", "homestead", "cozy", "永恒的mc", "落石"], "Grass.png", "探索"),
    (["空岛", "天空", "sky", "stoneblock"], "Cobblestone.png", "建筑"),
    (["落幕", "刀剑", "沉浸", "魔之", "殉道", "远梦", "匠心", "推荐", "十大神包", "我的世界2.0", "minecraft", "2000万", "凡人修仙"], "GoldBlock.png", "热门"),
]

def classify_icon(title, name):
    """根据名称判断整合包类型，返回适合的图标文件名"""
    combined = (title + " " + name).lower()
    for keywords, icon, _ in CATEGORY_MAP:
        for kw in keywords:
            if kw in combined:
                return icon
    return "Grass.png"

# 合辑关键词 - 匹配这些的都不是单个整合包推荐
COMPILATION_KW = ["推荐", "10款", "5个", "TOP", "盘点", "系列",
                    "上半年", "下半年", "必玩", "神包", "排行"]

def is_compilation(title, name):
    """检查是否为多包合辑视频"""
    combined = (title + " " + name).lower()
    count = sum(1 for kw in COMPILATION_KW if kw.lower() in combined)
    return count >= 2  # 匹配到2个以上合辑关键词才判定

def short_name(d):
    """返回 (title, url, icon_file) 三元组"""
    plat = d.get("platform", "")
    name = d.get("name", "")
    url = d.get("url", "")
    
    if plat == "bilibili":
        views = int(d.get("views", 0) or 0)
        w = f"{views//10000}万" if views >= 10000 else str(views)
        # 跳过合辑视频
        if is_compilation(name, name):
            return "", "", ""
        # 提取简短名称
        for kw in ["乌托邦", "中世纪", "落幕曲", "勇者之章", "愚者", "RLCraft",
                    "格雷", "森罗万藏", "咒次元", "刀剑", "沉浸战斗", "魔之逆鳞",
                    "殉道之路", "远梦之棺", "永恒的MC", "凡人修仙", "Prehistoric",
                    "龙之冒险", "Homestead", "宝可梦", "方可梦", "更好的MC",
                    "我的世界2.0", "方块宝可梦", "2000万", "炸裂", "十大神包",
                    "冒险向", "双人德爷"]:
            if kw in name:
                idx = name.index(kw)
                n = name[idx:idx+20].split("！")[0].split("，")[0][:12]
                title = f"{n} · {w}"
                return title, url, classify_icon(title, name)
        n = name.split("！")[0].split("，")[0][:14].strip("【】")
        title = f"{n} · {w}"
        return title, url, classify_icon(title, name)
    else:
        nm = name[:22]
        if "Better MC [FORGE] - BMC4" in nm: nm = "Better MC [FORGE]"
        elif "Better MC [FABRIC] - BMC2" in nm: nm = "Better MC [FABRIC]"
        elif "All the Mods 10 - ATM10" in nm: nm = "All The Mods 10"
        elif "[FABRIC]" in nm: nm = nm.replace(" [FABRIC]", "")
        elif "[FORGE]" in nm: nm = nm.replace(" [FORGE]", "")
        return nm, url, classify_icon(nm, name)


def info_picker(url):
    if "bilibili.com/video" in url: return "▸ 🎬B站 · 热门"
    if "curseforge" in url: return "▸ 📥CurseForge"
    return "▸ 📥Modrinth"

def make_column(items, col_key, icon_w=18, video_mode=False):
    """生成一列条目。items 为 (title, url, icon_file) 三元组。video_mode=True 时忽略 icon_file 使用自带图标"""
    xml = f'               <StackPanel Grid.Column="{col_key}">\n'
    for item in items:
        if video_mode:
            title, url, ico = item
            info = "▸ 点击前往 B站观看"
        else:
            title, url, ico = item
            info = info_picker(url)
        title = title.replace('"', "'").replace("&", "&amp;")
        xml += f'''          <Grid Margin="-2,0,10,2" VerticalAlignment="Center">
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="22" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <local:MyImage Grid.Column="0" Width="{icon_w}" Height="{icon_w}"
                    Source="pack://application:,,,/images/Blocks/{ico}"
                    VerticalAlignment="Center" HorizontalAlignment="Left" />
               <local:MyListItem Grid.Column="1"
                    Title="{title}"
                    Info="{info}"
                    EventType="打开网页"
                    EventData="{url}"
                    Type="Clickable" />
          </Grid>
'''
    xml += "               </StackPanel>\n"
    return xml


def main():
    log("=== PCL2 主页自动更新开始 ===")

    data_path = os.path.join(BASE, "modpacks_data.json")
    if not os.path.exists(data_path):
        log(f"ERROR: {data_path} 不存在")
        return 1

    with open(data_path) as f:
        data = json.load(f)

    # 过滤合辑视频（只保留单个整合包推荐）
    bili_raw = [d for d in data if d.get("platform") == "bilibili"]
    comp_kw = ["推荐", "10款", "5个", "TOP", "盘点", "系列", "上半年", "下半年", "必玩", "神包", "排行"]
    bili_raw_filtered = []
    for d in bili_raw:
        name = d.get('name', '')
        match_count = sum(1 for kw in comp_kw if kw in name)
        if match_count == 0:  # 匹配到合辑关键词就跳过
            bili_raw_filtered.append(d)
    print(f'Bilibili: {len(bili_raw)} raw → {len(bili_raw_filtered)} after compilation filter')
    bilibili = sorted(
        bili_raw_filtered,
        key=lambda x: int(x.get("views", 0) or 0), reverse=True
    )
    cm_all = sorted(
        [d for d in data if d.get("platform") in ("curseforge", "modrinth")],
        key=lambda x: int(x.get("downloads", 0) or 0), reverse=True
    )

    # === 整合包推荐 - 3列 ===
    # 第1列: 高播放 B站整合包
    c0 = [short_name(bilibili[i]) for i in [0,1,3,5,10,2,4,6,8,14]]
    # 第2列: B站更多 + CF/Modrinth 混排
    c2 = [short_name(bilibili[i]) for i in [11,12,13,7,9,15]] + [short_name(cm_all[i]) for i in [4,7,12]]
    # 第3列: CurseForge/Modrinth 热门
    c4 = [short_name(cm_all[i]) for i in [0,1,2,3,9,10,11,16,20,30]]

    modpack_xml = '''<!-- ================================ -->
<!--  🏗 整合包推荐 · 方块精选   -->
<!-- ================================ -->
<local:MyCard Margin="0,0,0,20" Title="">
     <StackPanel Margin="24,35,24,18">
          <TextBlock Text="整合包推荐" FontSize="22" FontWeight="Bold"
               Foreground="{DynamicResource ColorBrush1}"
               HorizontalAlignment="Center" Margin="0,0,0,12" />
          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="10" />
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="10" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
'''
    modpack_xml += make_column(c0, 0)
    modpack_xml += make_column(c2, 2)
    modpack_xml += make_column(c4, 4)
    modpack_xml += '''          </Grid>
     </StackPanel>
</local:MyCard>'''

    # === 视频推荐 - 3列 ===
    col1_v = [
        ("籽岷 · MC模组推荐合集", "https://space.bilibili.com/686127/video", "Grass.png"),
        ("黑山大叔 · 红石科技", "https://space.bilibili.com/19428259/video", "RedstoneBlock.png"),
        ("老迪来咯 · MC搞笑实况", "https://space.bilibili.com/27996286/video", "GoldBlock.png"),
        ("🔥 乌托邦探险3.2 365万", "https://www.bilibili.com/video/BV1Kf421X7cg", "Cobblestone.png"),
        ("🔥 中世纪王国100天 364万", "https://www.bilibili.com/video/BV1bE421P7zG", "Anvil.png"),
        ("🔥 落幕曲 · 268万", "https://www.bilibili.com/video/BV1etG5zCEvm", "CommandBlock.png"),
        ("🔥 方块宝可梦ZA 255万", "https://www.bilibili.com/video/BV1VNLRzYERC", "RedstoneLampOn.png"),
        ("🔥 勇者之章3 · 201万", "https://www.bilibili.com/video/BV11N2JBCEbv", "Egg.png"),
        ("🔥 年度十大神包 289万", "https://www.bilibili.com/video/BV1p1421C75Q", "Fabric.png"),
    ]
    col2_v = [
        ("Nor叔 · MC极限生存", "https://space.bilibili.com/17425003/video", "Cobblestone.png"),
        ("大炒面 · MC热门", "https://space.bilibili.com/14890801/video", "Anvil.png"),
        ("河狸 · 整合包实况", "https://space.bilibili.com/1451042208/video", "RedstoneLampOn.png"),
        ("🔥 炸裂整合包 233万", "https://www.bilibili.com/video/BV1CK3JzgESC", "Egg.png"),
        ("🔥 10款冒险向 215万", "https://www.bilibili.com/video/BV1J24y1R7GT", "Fabric.png"),
        ("🔥 愚者 · 171万", "https://www.bilibili.com/video/BV1AoVwzFEnN", "Grass.png"),
        ("🔥 RLCraft · 171万", "https://www.bilibili.com/video/BV1SY4y1j7kr", "RedstoneBlock.png"),
        ("🔥 更好的MC 176万", "https://www.bilibili.com/video/BV1DrE2z1EcF", "GoldBlock.png"),
        ("🔥 2000万下载 259万", "https://www.bilibili.com/video/BV15M4m127dH", "CommandBlock.png"),
    ]
    col3_v = [
        ("小鲨鱼 · 整合包推荐", "https://space.bilibili.com/1110881400/video", "Fabric.png"),
        ("GW漫游 · 游戏杂谈", "https://space.bilibili.com/2240562/video", "Egg.png"),
        ("MC热门搜索", "https://search.bilibili.com/all?keyword=Minecraft+整合包+推荐", "RedstoneLampOn.png"),
        ("我的世界搞笑", "https://search.bilibili.com/all?keyword=我的世界+搞笑", "Grass.png"),
        ("MC速通世界纪录", "https://search.bilibili.com/all?keyword=Minecraft+速通", "RedstoneBlock.png"),
        ("建筑欣赏", "https://search.bilibili.com/all?keyword=我的世界+建筑", "GoldBlock.png"),
        ("MC红石机械动力", "https://search.bilibili.com/all?keyword=Create+机械动力", "Cobblestone.png"),
        ("MC宝可梦世界", "https://search.bilibili.com/all?keyword=MC+宝可梦+整合包", "Anvil.png"),
        ("MC魔法冒险", "https://search.bilibili.com/all?keyword=Minecraft+魔法+整合包", "CommandBlock.png"),
    ]

    video_xml = '''<!-- ================================ -->
<!--  🎬 视频推荐 · 映像大厅   -->
<!-- ================================ -->
<local:MyCard Margin="0,0,0,20" Title="">
     <StackPanel Margin="24,32,24,18">
          <TextBlock Text="视频推荐" FontSize="22" FontWeight="Bold"
               Foreground="{DynamicResource ColorBrush1}"
               HorizontalAlignment="Center" Margin="0,0,0,10" />
<Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="16" />
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="16" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
'''
    for col_idx, items in [(0, col1_v), (2, col2_v), (4, col3_v)]:
        video_xml += make_column(items, col_idx, icon_w=16, video_mode=True)

    video_xml += '''          </Grid>
     </StackPanel>
</local:MyCard>'''

    # === 应用到文件 ===
    xaml_path = os.path.join(OUTPUT, "Custom.xaml")
    with open(xaml_path) as f:
        content = f.read()

    # 替换整合包推荐区块
    modpack_re = r'<!-- ================================ -->\n<!--  🏗 整合包推荐 · 方块精选   -->\n<!-- ================================ -->\n<local:MyCard.*?</local:MyCard>'
    content = re.sub(modpack_re, modpack_xml, content, flags=re.DOTALL, count=1)

    # 替换视频推荐区块
    video_re = r'<!-- ================================ -->\n<!--  🎬 视频推荐 · 映像大厅   -->\n<!-- ================================ -->\n<local:MyCard.*?</local:MyCard>'
    content = re.sub(video_re, video_xml, content, flags=re.DOTALL, count=1)

    # 更新时间戳
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M")
    content = re.sub(r"更新: \d{4}-\d{2}-\d{2} \d{2}:\d{2}", f"更新: {ts}", content)

    with open(xaml_path, "w") as f:
        f.write(content)
    log(f"Custom.xaml 已更新 ({ts})")

    # 更新 version
    ver = f"v1.0.{now.month:02d}{now.day:02d}"
    with open(os.path.join(OUTPUT, "version.txt"), "w") as f:
        f.write(ver)
    log(f"version.txt → {ver}")

    # 计算 CRC
    with open(xaml_path, "rb") as f:
        data = f.read()
    crc = zlib.crc32(data) & 0xFFFFFFFF
    crc_ts = now.strftime("%d%H%M")
    with open(os.path.join(OUTPUT, "Custom.xaml.ini"), "w") as f:
        f.write(f"{crc_ts}:{crc:08x}")
    log(f"CRC → {crc_ts}:{crc:08x}")

    # === 同步 ===
    # Windows
    if os.path.isdir(WIN):
        for fn in ["Custom.xaml", "Custom.xaml.ini", "version.txt"]:
            shutil.copy2(os.path.join(OUTPUT, fn), os.path.join(WIN, fn))
        log("Windows 同步完成")
    else:
        log(f"WARNING: Windows 目录 {WIN} 不存在")

    # 服务器
    if os.path.isfile(SSH_KEY):
        import subprocess
        for fn in ["Custom.xaml", "Custom.xaml.ini", "version.txt"]:
            src = os.path.join(OUTPUT, fn)
            cmd = ["scp", "-i", SSH_KEY, src, f"{SERVER}:{SERVER_PATH}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                log(f"ERROR: 服务器 {fn} 同步失败: {result.stderr}")
            else:
                log(f"服务器 {fn} 同步完成")
    else:
        log(f"WARNING: SSH 密钥 {SSH_KEY} 不存在")

    log("=== PCL2 主页自动更新结束 ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())

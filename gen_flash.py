import re, zlib
from datetime import datetime

XAML = '/home/ftc13/pcl2/output/Custom.xaml'
WIN = '/mnt/d/pcl/PCL/Custom.xaml'
now = datetime.now()
ts = now.strftime('%Y-%m-%d %H:%M')
BR1 = "{DynamicResource ColorBrush1}"
BR5 = "{DynamicResource ColorBrush5}"

# Read current file to extract all items
with open(XAML) as f:
    old = f.read()

items = re.findall(r'Title="([^"]+)"\s+Info="([^"]*)"\s+EventType="打开网页"\s+EventData="([^"]+)"', old)
up, vid, cf = [], [], []
for t,i,u in items:
    if not t: continue
    if 'space.bilibili.com' in u: up.append((t,u))
    elif 'curseforge' in u or 'modrinth' in u: cf.append((t,u))
    else: vid.append((t,u))

# Deduplicate
seen_v = set()
vid_dedup = []
for t,u in vid:
    if u not in seen_v: seen_v.add(u); vid_dedup.append((t,u))

# Icon selection
def ico(t):
    tl = t.lower()
    if any(k in tl for k in ['宝可梦','pixelmon','cobblemon','pokemon','egg']): return 'Egg.png'
    if any(k in tl for k in ['红石','create','机械','fabulously','sodium','craftoria','opti','stoneblock','科技']): return 'RedstoneBlock.png'
    if any(k in tl for k in ['恐怖','rlcraft','dread','zombie','horror','deceased','backrooms','cave','nightfall']): return 'CommandBlock.png'
    if any(k in tl for k in ['冒险','勇者','龙','prehistoric','dawncraft','mc鱼本','双人德爷','anvil']): return 'Anvil.png'
    if any(k in tl for k in ['魔法','愚者','fantasy','咒','prominence','lamp']): return 'RedstoneLampOn.png'
    if any(k in tl for k in ['乌托邦','中世纪','homestead','家园','cozy','grass']): return 'Grass.png'
    if any(k in tl for k in ['空岛','建筑','cobblestone','sky','八方','cobble']): return 'Cobblestone.png'
    if any(k in tl for k in ['落幕','刀剑','沉浸','魔之','殉道','远梦','匠心','籽岷','老迪','大炒','河狸','nor','gw漫游','小鲨鱼','黑山','频道','模组']): return 'GoldBlock.png'
    return 'Fabric.png'

def item(title, url, icon, info, sz=14):
    t = title.replace('"', "'").replace('&', '&amp;')
    return f'''          <Grid Margin="-1,0,8,1" VerticalAlignment="Center">
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="18" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <local:MyImage Grid.Column="0" Width="{sz}" Height="{sz}"
                    Source="pack://application:,,,/images/Blocks/{icon}"
                    VerticalAlignment="Center" HorizontalAlignment="Left" />
               <local:MyListItem Grid.Column="1"
                    Title="{t}"
                    Info="{info}"
                    EventType="打开网页"
                    EventData="{url}"
                    Type="Clickable" />
          </Grid>'''

# Icon separator bar
def sep():
    ics = ['Grass.png','RedstoneBlock.png','GoldBlock.png','Cobblestone.png','Anvil.png',
           'CommandBlock.png','RedstoneLampOn.png','Egg.png','Fabric.png',
           'GoldBlock.png','RedstoneBlock.png','Grass.png']
    s = '          <StackPanel Orientation="Horizontal" HorizontalAlignment="Center" Margin="0,5,0,3">\n'
    for ic in ics:
        s += f'               <local:MyImage Width="9" Height="9" Margin="1.5,0" Source="pack://application:,,,/images/Blocks/{ic}" />\n'
    s += '          </StackPanel>\n'
    return s

# Section header with icons
def hdr(text, emoji="⬡"):
    return f'''          <StackPanel Orientation="Horizontal" HorizontalAlignment="Center" Margin="0,0,0,8">
               <local:MyImage Width="12" Height="12" Margin="0,0,5,0" VerticalAlignment="Center" Source="pack://application:,,,/images/Blocks/GoldBlock.png" />
               <TextBlock Text="{emoji} {text} {emoji}" FontSize="15" FontWeight="Bold" Foreground="{BR1}" VerticalAlignment="Center" />
               <local:MyImage Width="12" Height="12" Margin="5,0,0,0" VerticalAlignment="Center" Source="pack://application:,,,/images/Blocks/GoldBlock.png" />
          </StackPanel>'''

ICON_SET = ['Grass.png','RedstoneBlock.png','GoldBlock.png','Cobblestone.png','Anvil.png','CommandBlock.png','RedstoneLampOn.png','Egg.png','Fabric.png',
            'Grass.png','RedstoneBlock.png','GoldBlock.png','Cobblestone.png','Anvil.png','CommandBlock.png','RedstoneLampOn.png','Egg.png','Fabric.png']

# Build
xaml = f'''<!--
  ====================================================
   ⚔ PCL 整合包推荐引擎 · 幻彩版
   更新: {ts}
  ====================================================
-->
<local:MyCard Margin="0,0,0,12" Title="">
     <StackPanel Margin="0,10,0,8">
          {sep()}
          <StackPanel Orientation="Horizontal" HorizontalAlignment="Center">
               <local:MyImage Width="18" Height="18" Margin="0,0,6,0" VerticalAlignment="Center" Source="pack://application:,,,/images/Blocks/GoldBlock.png" />
               <local:MyImage Width="18" Height="18" Margin="0,0,2,0" VerticalAlignment="Center" Source="pack://application:,,,/images/Blocks/RedstoneBlock.png" />
               <TextBlock Text="⚔ PCL 整合包推荐引擎 ⚔" FontSize="22" FontWeight="Bold" Foreground="{BR1}" VerticalAlignment="Center" />
               <local:MyImage Width="18" Height="18" Margin="2,0,0,0" VerticalAlignment="Center" Source="pack://application:,,,/images/Blocks/RedstoneBlock.png" />
               <local:MyImage Width="18" Height="18" Margin="6,0,0,0" VerticalAlignment="Center" Source="pack://application:,,,/images/Blocks/GoldBlock.png" />
          </StackPanel>
          <TextBlock Text="聚合 B站 · CurseForge · Modrinth" FontSize="9" Foreground="{BR5}" HorizontalAlignment="Center" Margin="0,2,0,0" />
          {sep()}
     </StackPanel>
</local:MyCard>
'''

# 3 columns layout for modpack area - mix videos + CF
all_mix = []
hi, ci = 0, 0
while hi < len(vid_dedup) or ci < len(cf):
    if hi < len(vid_dedup): all_mix.append(('v', vid_dedup[hi])); hi += 1
    if ci < len(cf): all_mix.append(('c', cf[ci])); ci += 1

cols = [[], [], []]
for i, (typ, (t, u)) in enumerate(all_mix):
    cols[i % 3].append((t, u, typ))

# Modpack section
xaml += f'''<local:MyCard Margin="0,0,0,12" Title="">
     <StackPanel Margin="16,16,12,12">
          {hdr("整合包推荐", "🛡")}
          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="10" />
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="10" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
'''
for ci_idx in range(3):
    xaml += f'               <StackPanel Grid.Column="{ci_idx * 2}">\n'
    for j, (t, u, typ) in enumerate(cols[ci_idx]):
        ic = ico(t)
        inf = "▸ 🎬B站 · 热门" if typ == 'v' else ("▸ 📥CurseForge" if 'curseforge' in u else "▸ 📥Modrinth")
        xaml += item(t, u, ic, inf)
    xaml += '               </StackPanel>\n'
xaml += '''          </Grid>
     </StackPanel>
</local:MyCard>
'''

# Video section
vid_chunks = [vid_dedup[i:i+8] for i in range(0, min(len(vid_dedup), 24), 8)]
xaml += f'''<local:MyCard Margin="0,0,0,12" Title="">
     <StackPanel Margin="16,16,12,12">
          {hdr("热门视频", "🎬")}
          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="10" />
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="10" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
'''
for ci_idx in range(3):
    xaml += f'               <StackPanel Grid.Column="{ci_idx * 2}">\n'
    for j, (t, u) in enumerate(vid_chunks[ci_idx] if ci_idx < len(vid_chunks) else []):
        ic = ico(t)
        xaml += item(t, u, ic, "▸ 🎬B站 · 热门", 13)
    xaml += '               </StackPanel>\n'
xaml += '''          </Grid>
     </StackPanel>
</local:MyCard>
'''

# UP section
up_half = len(up) // 2
xaml += f'''<local:MyCard Margin="0,0,0,12" Title="">
     <StackPanel Margin="16,16,12,12">
          {hdr("UP 主推荐", "🎮")}
          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="10" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <StackPanel Grid.Column="0">
'''
uicons = ['Grass.png','RedstoneBlock.png','GoldBlock.png','Cobblestone.png','Anvil.png','CommandBlock.png','RedstoneLampOn.png','Egg.png']
for i, (t, u) in enumerate(up[:up_half]):
    xaml += item(t, u, uicons[i % len(uicons)], "▸ 前往 B站", 13)
xaml += '''               </StackPanel>
               <StackPanel Grid.Column="2">
'''
for i, (t, u) in enumerate(up[up_half:]):
    xaml += item(t, u, uicons[(i+up_half) % len(uicons)], "▸ 前往 B站", 13)
xaml += '''               </StackPanel>
          </Grid>
     </StackPanel>
</local:MyCard>
'''

# Latest section
latest = vid_dedup[:3] if len(vid_dedup) >= 3 else vid_dedup
licons = ['Egg.png', 'RedstoneBlock.png', 'CommandBlock.png']
xaml += f'''<local:MyCard Margin="0,0,0,12" Title="">
     <StackPanel Margin="16,12,12,12">
          {hdr("最新发布 · 值得一看", "🔥")}
          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="12" />
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="12" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
'''
for ci_idx in range(3):
    xaml += f'               <StackPanel Grid.Column="{ci_idx * 2}">\n'
    if ci_idx < len(latest):
        t, u = latest[ci_idx]
        xaml += item(t, u, licons[ci_idx], "▸ 🎬 最新发布", 14)
    xaml += '               </StackPanel>\n'
xaml += '''          </Grid>
     </StackPanel>
</local:MyCard>
'''

# About section
xaml += f'''<local:MyCard Margin="0,0,0,0" Title="">
     <StackPanel>
          {sep()}
          <Grid Margin="20,8,14,14">
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="Auto" />
               </Grid.ColumnDefinitions>
               <StackPanel Grid.Column="0" VerticalAlignment="Center">
                    <StackPanel Orientation="Horizontal">
                         <TextBlock Text="⚔ PCL" FontSize="18" Foreground="{BR1}" FontWeight="Bold" VerticalAlignment="Center" />
                         <TextBlock Text=" 整合包推荐引擎 ⚔" FontSize="18" FontWeight="Bold" Foreground="{BR1}" VerticalAlignment="Center" />
                    </StackPanel>
                    <StackPanel Orientation="Horizontal" Margin="0,2,0,0">
                         <TextBlock Text="By GDSGDHG" FontSize="10" Foreground="{BR5}" FontWeight="Bold" />
                         <TextBlock Text=" · " FontSize="10" Foreground="{BR5}" VerticalAlignment="Center" />
                         <TextBlock Text="数据源: B站 · BBSMC · CurseForge · Modrinth" FontSize="10" Foreground="{BR5}" VerticalAlignment="Center" />
                    </StackPanel>
               </StackPanel>
               <StackPanel Grid.Column="1" VerticalAlignment="Center">
                    <local:MyListItem
                         Title="📮 反馈"
                         EventType="打开网页"
                         EventData="https://github.com/Meloong-Git/PCL/discussions/8588"
                         Type="Clickable" />
               </StackPanel>
          </Grid>
          {sep()}
     </StackPanel>
</local:MyCard>
'''

# Write
with open(XAML, 'w') as f:
    f.write(xaml)

with open(XAML, 'rb') as f:
    d = f.read()
crc = zlib.crc32(d) & 0xFFFFFFFF

with open(WIN, 'w') as f:
    f.write(xaml)
with open('/mnt/d/pcl/PCL/Custom.xaml.ini', 'w') as f:
    f.write(f'242048:{crc:08x}')
with open('/home/ftc13/pcl2/output/Custom.xaml.ini', 'w') as f:
    f.write(f'242048:{crc:08x}')

print(f"生成了: {len(xaml)} 字符")
print(f"CRC: 242048:{crc:08x}")
print(f"本地 D:\\pcl\\PCL\\Custom.xaml ✅")
print(f"服务器: 未同步 ⚠️")

# Validate
for tag in ['local:MyCard', 'Grid']:
    o = xaml.count(f'<{tag}>') + xaml.count(f'<{tag} ')
    cl = xaml.count(f'</{tag}>')
    print(f'{tag}: {o}/{cl} {"OK" if o==cl else "BAD"} ')

bads = xaml.count('DynamicResource ColorBrush')
print(f'Bare ColorBrush: {bads} {"OK" if bads==0 else "BAD"} ')

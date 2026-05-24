import json, zlib, re
from datetime import datetime

with open('/tmp/flash_data.json') as f:
    data = json.load(f)

up_items = data['up']
hot_items = data['hot']
cf_items = data['cf']

now = datetime.now()
ts = now.strftime('%Y-%m-%d %H:%M')
BR1 = "{DynamicResource ColorBrush1}"
BR5 = "{DynamicResource ColorBrush5}"

def item(title, url, icon, info, icon_size=16):
    t = title.replace('"', "'").replace('&', '&amp;')
    return f'''          <Grid Margin="-1,0,8,1" VerticalAlignment="Center">
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="20" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <local:MyImage Grid.Column="0" Width="{icon_size}" Height="{icon_size}"
                    Source="pack://application:,,,/images/Blocks/{icon}"
                    VerticalAlignment="Center" HorizontalAlignment="Left" />
               <local:MyListItem Grid.Column="1"
                    Title="{t}"
                    Info="{info}"
                    EventType="打开网页"
                    EventData="{url}"
                    Type="Clickable" />
          </Grid>'''

def icon_for(t):
    tl = t.lower()
    if any(k in tl for k in ['宝可梦','pixelmon','cobblemon','pokemon']): return 'Egg.png'
    if any(k in tl for k in ['红石','create','机械','fabulously','sodium','craftoria','opti','stoneblock','科技']): return 'RedstoneBlock.png'
    if any(k in tl for k in ['恐怖','rlcraft','dread','zombie','horror','deceased','backrooms','cave','nightfall']): return 'CommandBlock.png'
    if any(k in tl for k in ['冒险','勇者','龙','prehistoric','dawncraft','mc鱼本','双人德爷']): return 'Anvil.png'
    if any(k in tl for k in ['魔法','愚者','fantasy','咒','prominence']): return 'RedstoneLampOn.png'
    if any(k in tl for k in ['乌托邦','中世纪','homestead','家园','cozy']): return 'Grass.png'
    if any(k in tl for k in ['空岛','建筑','cobblestone','sky','八方']): return 'Cobblestone.png'
    if any(k in tl for k in ['落幕','刀剑','沉浸','魔之','殉道','远梦','匠心','籽岷','up','频道','模组']): return 'GoldBlock.png'
    return 'Fabric.png'

def icon_sep():
    icons = ['Grass.png','RedstoneBlock.png','GoldBlock.png','Cobblestone.png','Anvil.png',
             'CommandBlock.png','RedstoneLampOn.png','Egg.png','Fabric.png',
             'GoldBlock.png','RedstoneBlock.png','Grass.png']
    line = '          <StackPanel Orientation="Horizontal" HorizontalAlignment="Center" Margin="0,6,0,4">\n'
    for ico in icons:
        line += f'               <local:MyImage Width="10" Height="10" Margin="2,0" Source="pack://application:,,,/images/Blocks/{ico}" />\n'
    line += '          </StackPanel>\n'
    return line

def section_header(text, emoji="⬡"):
    return f'''          <StackPanel Orientation="Horizontal" HorizontalAlignment="Center" Margin="0,0,0,8">
               <local:MyImage Width="14" Height="14" Margin="0,0,6,0" VerticalAlignment="Center"
                    Source="pack://application:,,,/images/Blocks/GoldBlock.png" />
               <TextBlock Text="{emoji} {text} {emoji}" FontSize="16" FontWeight="Bold"
                    Foreground="{BR1}"
                    VerticalAlignment="Center" />
               <local:MyImage Width="14" Height="14" Margin="6,0,0,0" VerticalAlignment="Center"
                    Source="pack://application:,,,/images/Blocks/GoldBlock.png" />
          </StackPanel>'''

# Build
xaml = f'''<!--
  ======================================================
   PCL 整合包推荐引擎 · 幻彩版
   更新: {ts}
  ======================================================
-->
<local:MyCard Margin="0,0,0,14" Title="">
     <StackPanel Margin="0,12,0,10">
          {icon_sep()}
          <TextBlock Text="⚔ PCL 整合包推荐引擎 ⚔" FontSize="24" FontWeight="Bold"
               Foreground="{BR1}"
               HorizontalAlignment="Center" />
          <TextBlock Text="聚合 B站 · CurseForge · Modrinth · BBSMC" FontSize="9"
               Foreground="{BR5}"
               HorizontalAlignment="Center" Margin="0,2,0,0" />
          {icon_sep()}
     </StackPanel>
</local:MyCard>

<local:MyCard Margin="0,0,0,14" Title="">
     <StackPanel Margin="18,18,14,14">
          {section_header("整合包推荐", "🛡")}
          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="10" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <StackPanel Grid.Column="0">
'''
all_mix = []
hi, ci = 0, 0
while hi < len(hot_items) or ci < len(cf_items):
    if hi < len(hot_items):
        all_mix.append(('hot', hot_items[hi]))
        hi += 1
    if ci < len(cf_items):
        all_mix.append(('cf', cf_items[ci]))
        ci += 1

col1, col2 = [], []
for i, mix_item in enumerate(all_mix):
    (col1 if i % 2 == 0 else col2).append(mix_item)

for typ, (t, info, u) in col1:
    xaml += item(t, u, icon_for(t), info)
xaml += '''               </StackPanel>
               <StackPanel Grid.Column="2">
'''
for typ, (t, info, u) in col2:
    xaml += item(t, u, icon_for(t), info)
xaml += '''               </StackPanel>
          </Grid>
     </StackPanel>
</local:MyCard>

<local:MyCard Margin="0,0,0,14" Title="">
     <StackPanel Margin="18,18,14,14">
          {section_header("热门视频", "🎬")}
          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="12" />
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="12" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <StackPanel Grid.Column="0">
'''
cols = [[], [], []]
for i, (t, info, u) in enumerate(hot_items[:24]):
    cols[i % 3].append((t, info, u))

for idx in range(3):
    if idx > 0:
        xaml += f'''               <StackPanel Grid.Column="{idx * 2}">
'''
    for t, info, u in cols[idx]:
        xaml += item(t, u, icon_for(t), info, 14)
    xaml += '               </StackPanel>\n'

xaml += f'''          </Grid>
     </StackPanel>
</local:MyCard>

<local:MyCard Margin="0,0,0,14" Title="">
     <StackPanel Margin="18,18,14,14">
          {section_header("UP 主推荐", "🎮")}
          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="10" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <StackPanel Grid.Column="0">
'''
up_icons = ['Grass.png','RedstoneBlock.png','GoldBlock.png','Cobblestone.png',
            'Anvil.png','CommandBlock.png','RedstoneLampOn.png','Egg.png']
uh = len(up_items) // 2
for i, (t, info, u) in enumerate(up_items[:uh]):
    xaml += item(t, u, up_icons[i % len(up_icons)], info, 14)
xaml += '''               </StackPanel>
               <StackPanel Grid.Column="2">
'''
for i, (t, info, u) in enumerate(up_items[uh:]):
    xaml += item(t, u, up_icons[(i+uh) % len(up_icons)], info, 14)
xaml += '''               </StackPanel>
          </Grid>
     </StackPanel>
</local:MyCard>

<local:MyCard Margin="0,0,0,14" Title="">
     <StackPanel Margin="18,14,14,14">
          {section_header("最新发布 · 值得一看", "🔥")}
          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="12" />
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="12" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
'''
latest = hot_items[24:27] if len(hot_items) > 24 else hot_items[:3]
latest_icons = ['Egg.png', 'RedstoneBlock.png', 'CommandBlock.png']
for idx in range(3):
    col = idx * 2
    xaml += f'               <StackPanel Grid.Column="{col}">\n'
    if idx < len(latest):
        t, info, u = latest[idx]
        xaml += item(t, u, latest_icons[idx], "▸ 🎬 最新发布", 16)
    xaml += '               </StackPanel>\n'

xaml += '''          </Grid>
     </StackPanel>
</local:MyCard>

<local:MyCard Margin="0,0,0,0" Title="">
     <StackPanel>
          ''' + icon_sep() + '''
          <Grid Margin="20,8,14,14">
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="Auto" />
               </Grid.ColumnDefinitions>
               <StackPanel Grid.Column="0" VerticalAlignment="Center">
                    <StackPanel Orientation="Horizontal">
                         <TextBlock Text="⚔ PCL" FontSize="18"
                              Foreground="''' + BR1 + '''" FontWeight="Bold" VerticalAlignment="Center" />
                         <TextBlock Text=" 整合包推荐引擎 ⚔" 
                              FontSize="18" FontWeight="Bold"
                              Foreground="''' + BR1 + '''" VerticalAlignment="Center" />
                    </StackPanel>
                    <StackPanel Orientation="Horizontal" Margin="0,4,0,0">
                         <TextBlock Text="By GDSGDHG" FontSize="10"
                              Foreground="''' + BR5 + '''" FontWeight="Bold" />
                         <TextBlock Text=" · " FontSize="10"
                              Foreground="''' + BR5 + '''" VerticalAlignment="Center" />
                         <TextBlock Text="数据源: B站 · BBSMC · CurseForge · Modrinth" FontSize="10"
                              Foreground="''' + BR5 + '''" VerticalAlignment="Center" />
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
          ''' + icon_sep() + '''
     </StackPanel>
</local:MyCard>
'''

outpath = '/home/ftc13/pcl2/output/Custom.xaml'
with open(outpath, 'w') as f:
    f.write(xaml)

with open(outpath, 'rb') as f:
    d = f.read()
crc = zlib.crc32(d) & 0xFFFFFFFF

win_path = '/mnt/d/pcl/PCL/Custom.xaml'
with open(win_path, 'w') as f:
    f.write(xaml)

with open('/mnt/d/pcl/PCL/Custom.xaml.ini', 'w') as f:
    f.write(f'242042:{crc:08x}')
with open('/home/ftc13/pcl2/output/Custom.xaml.ini', 'w') as f:
    f.write(f'242042:{crc:08x}')

print(f"CR: {len(xaml)} chars")
print("CRC: 242042:" + hex(crc)[2:])
print("Windows D:\\pcl\\PCL\\Custom.xaml ok")
print("⚠ 服务器未同步")

for tag in ['MyCard', 'Grid']:
    o = xaml.count(f'<{tag}>') + xaml.count(f'<{tag} ')
    cl = xaml.count(f'</{tag}>')
    print(f'{tag}: {o}/{cl} {"ok" if o==cl else "BAD"}')

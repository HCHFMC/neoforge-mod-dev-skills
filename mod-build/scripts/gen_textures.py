# gen_textures.py — SolarMod 纹理生成系统
# Level 1: 材质函数 → Level 2: UV 图集 → Level 3: 模型绑定
# 遵循 docmd/design/modeling_texturing_scheme.md 调色板与规范

import struct, zlib, random

# ============================================================
# 基础设施
# ============================================================

def hex2rgb(h):
    """#A8B0BC → (168, 176, 188)"""
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb2hex(r, g, b):
    return f'#{r:02X}{g:02X}{b:02X}'

def _clamp(v):
    return max(0, min(255, v))

def lighten(c, pct):
    """向白调亮 pct%"""
    return tuple(_clamp(v + int((255 - v) * pct / 100)) for v in c)

def darken(c, pct):
    """向黑调暗 pct%"""
    return tuple(_clamp(v - int(v * pct / 100)) for v in c)

def warm_shift(c, amt):
    """暖色调偏移：+R, +G, -B"""
    return (_clamp(c[0] + amt), _clamp(c[1] + amt // 2), _clamp(c[2] - amt))

def cool_shift(c, amt):
    """冷色调偏移：-R, -G, +B"""
    return (_clamp(c[0] - amt), _clamp(c[1] - amt // 2), _clamp(c[2] + amt))

def jitter(c, pct):
    """颜色随机偏移 pct%"""
    r = c[0] + random.randint(-int(c[0] * pct / 100), int(c[0] * pct / 100))
    g = c[1] + random.randint(-int(c[1] * pct / 100), int(c[1] * pct / 100))
    b = c[2] + random.randint(-int(c[2] * pct / 100), int(c[2] * pct / 100))
    return (_clamp(r), _clamp(g), _clamp(b))

def checker(c1, c2, x, y, size=2):
    """棋盘格过渡：返回 c1 或 c2"""
    return c1 if ((x // size) + (y // size)) % 2 == 0 else c2

def png(w, h, px, fn):
    """写入 RGBA PNG"""
    def c(t, d):
        x = t + d
        return struct.pack('>I', len(d)) + x + struct.pack('>I', zlib.crc32(x) & 0xFFFFFFFF)
    hdr = b'\x89PNG\r\n\x1a\n' + c(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    raw = b''
    for y in range(h):
        raw += b'\x00'
        for x in range(w):
            raw += bytes(px[y * w + x])
    with open(fn, 'wb') as f:
        f.write(hdr + c(b'IDAT', zlib.compress(raw)) + c(b'IEND', b''))

def solid_rect(px, canvas_w, x0, y0, w, h, color):
    """在像素数组上画纯色矩形"""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if 0 <= x < canvas_w and 0 <= y < canvas_w:
                px[y * canvas_w + x] = color

# ============================================================
# Level 1: 材质函数（维度无关）
# ============================================================

def metal_brushed(w, h, base, highlight=None, shadow=None, noise_pct=3):
    """拉丝金属：水平条纹 + 边缘明暗 + 微噪点
    base:     HEX 基底色
    highlight:HEX 高光色 (None=自动亮15%)
    shadow:   HEX 暗面色 (None=自动暗20%)
    noise_pct:噪声概率百分比
    """
    bc = hex2rgb(base)
    hl = hex2rgb(highlight) if highlight else lighten(bc, 15)
    sd = hex2rgb(shadow) if shadow else darken(bc, 20)

    px = []
    for y in range(h):
        for x in range(w):
            # 条纹：每隔 3px 一道微亮条纹
            color = hl if y % 3 == 0 else bc
            # 随机单像素噪点
            if random.random() < noise_pct / 100:
                color = jitter(color, 8)
            # 边缘明暗（定向光照：左上亮，右下暗）
            if y == 0:
                color = lighten(color, 20)
            if y == h - 1:
                color = darken(color, 25)
            if x == 0:
                color = lighten(color, 12)
            if x == w - 1:
                color = darken(color, 15)
            px.append(color)
    return px


def grid_panel(w, h, base, grid, cell=4, line=1):
    """电子面板网格：深底 + 浅色网格线 + 微噪声
    cell: 网格单元格大小 (px)
    line: 网格线宽度 (px)
    """
    bc = hex2rgb(base)
    gc = hex2rgb(grid)
    px = []
    for y in range(h):
        for x in range(w):
            if (x % cell < line) or (y % cell < line):
                color = gc
            else:
                color = bc
            # 单像素噪声
            if random.random() < 0.02:
                color = jitter(color, 8)
            # 边缘暗化
            if y == 0:
                color = darken(color, 12)
            if y == h - 1:
                color = darken(color, 18)
            if x == 0:
                color = darken(color, 8)
            if x == w - 1:
                color = darken(color, 12)
            px.append(color)
    return px


def brick_refractory(w, h, brick, mortar, brick_w=5, brick_h=3):
    """耐火砖：随机矩形砖块 + 深色接缝线
    brick_w/h: 砖块尺寸 (px)
    """
    bc = hex2rgb(brick)
    mc = hex2rgb(mortar)
    px = []
    for y in range(h):
        row_off = (y // brick_h) % 2 * (brick_w // 2)  # 交错偏移
        for x in range(w):
            bx_prime = (x - row_off) % brick_w if x >= row_off else x % brick_w
            if bx_prime == 0 or y % brick_h == 0:
                color = mc  # 接缝
            else:
                # 随机砖块颜色微变
                seed = (y // brick_h) * 100 + (x // brick_w)
                random.seed(seed)
                color = jitter(bc, 6)
            # 边缘暗化
            if y == 0:
                color = darken(color, 15)
            if y == h - 1:
                color = darken(color, 20)
            px.append(color)
    random.seed()  # reset
    return px


def leather_stitched(w, h, base, flap, stitch, buckle, flap_y=5):
    """皮革缝合：袋身底 + 翻盖顶 + 缝合线 + 搭扣 + 背带
    flap_y: 翻盖高度 (从 y=0 到 y=flap_y)
    """
    bc = hex2rgb(base)
    fc = hex2rgb(flap)
    sc = hex2rgb(stitch)
    bk = hex2rgb(buckle)
    px = []
    for y in range(h):
        for x in range(w):
            if y <= flap_y:
                # 翻盖区域
                color = fc
                # 缝合线
                if y == flap_y and x % 2 == 0:
                    color = sc
                # 搭扣 (居中, y=flap_y-1~flap_y+1)
                if flap_y - 1 <= y <= flap_y + 1 and w // 2 - 2 <= x <= w // 2 + 1:
                    color = bk
            else:
                # 袋身区域
                color = bc
                # 左右背带
                if x < w // 4:
                    color = darken(bc, 20)
                if x >= w * 3 // 4:
                    color = darken(bc, 20)
                # 前口袋
                if h // 3 <= y <= h * 2 // 3 and w // 4 <= x <= w * 3 // 4:
                    color = darken(bc, 10)
                    if x == w // 4:
                        color = sc  # 口袋边缝线
            # 边缘暗化
            if x == 0:
                color = darken(color, 10)
            if x == w - 1:
                color = darken(color, 15)
            px.append(color)
    return px


def card_gold(w, h, base, border, inner_border, icon, highlight):
    """金色卡片：外框 + 内框 + 中心图标 + 光泽点
    base: HEX 底色
    border: HEX 外框色
    inner_border: HEX 内框色
    icon: HEX 图标色
    highlight: HEX 高光点色
    """
    bc = hex2rgb(base)
    br = hex2rgb(border)
    ib = hex2rgb(inner_border)
    ic = hex2rgb(icon)
    hl = hex2rgb(highlight)
    px = []
    for y in range(h):
        for x in range(w):
            # 外边框 (1px)
            if x == 0 or x == w - 1 or y == 0 or y == h - 1:
                color = br
            # 内边框 (距边 2px, 1px)
            elif x == 2 or x == w - 3 or y == 2 or y == h - 3:
                color = ib
            # 中心菱形 (6×6)
            elif abs(x - w / 2) + abs(y - h / 2) < 3.5:
                color = ic
            # 左上光泽
            elif x <= w // 3 and y <= h // 3:
                color = hl
            # 右下暗角
            elif x >= 2 * w // 3 and y >= 2 * h // 3:
                color = darken(bc, 15)
            else:
                color = bc
            px.append(color)
    return px


# ============================================================
# Level 2: UV 图集布局
# ============================================================

def atlas_3face(w, h, top_config, side_config, bottom_config):
    """标准三面图集 (cube_bottom_top)
    返回 16×16 像素数组，分 3 垂直条带
    """
    px = [(0, 0, 0, 0)] * (w * h)
    top_h = h // 3
    side_h = h // 3
    bot_h = h - top_h - side_h

    # 顶面区域
    region = top_config['fn'](w, top_h, **top_config.get('args', {}))
    for y in range(top_h):
        for x in range(w):
            px[y * w + x] = region[y * w + x]

    # 侧面区域
    region = side_config['fn'](w, side_h, **side_config.get('args', {}))
    for y in range(side_h):
        for x in range(w):
            px[(top_h + y) * w + x] = region[y * w + x]

    # 底面区域
    region = bottom_config['fn'](w, bot_h, **bottom_config.get('args', {}))
    for y in range(bot_h):
        for x in range(w):
            px[(top_h + side_h + y) * w + x] = region[y * w + x]

    return px


def atlas_regions(w, h, regions):
    """通用 UV 图集：按区域字典填充
    regions: {(x0, y0, region_w, region_h): {'fn': fn, 'args': {...} }}
    """
    px = [(0, 0, 0, 0)] * (w * h)
    for (rx, ry, rw, rh), cfg in regions.items():
        region = cfg['fn'](rw, rh, **cfg.get('args', {}))
        for y in range(rh):
            for x in range(rw):
                if 0 <= rx + x < w and 0 <= ry + y < h:
                    px[(ry + y) * w + (rx + x)] = region[y * rw + x]
    return px


# ============================================================
# Level 3: 模型绑定
# ============================================================

def gen_wind_turbine():
    """风力发电机 UV 图集 16×16 — 遵循 §4.1 布局"""
    w, h = 16, 16
    regions = {
        # base: y=0-2, 底座
        (0, 0, w, 2): {'fn': metal_brushed, 'args': {'base': '#505A68', 'highlight': '#788290', 'shadow': '#404858'}},
        # pillar sides: y=2-10
        (0, 2, 4, 8): {'fn': metal_brushed, 'args': {'base': '#A8B0BC', 'highlight': '#D8DCE4', 'shadow': '#788290'}},
        # pillar up: y=2-4, x=4-16
        (4, 2, 12, 2): {'fn': metal_brushed, 'args': {'base': '#D8DCE4', 'highlight': '#E8ECF0', 'shadow': '#A8B0BC'}},
        # blade top: y=4-6, x=4-16
        (4, 4, 12, 2): {'fn': metal_brushed, 'args': {'base': '#94A3B8', 'highlight': '#B0B8C4', 'shadow': '#7C8FA0'}},
        # blade side: y=6-8, x=4-16
        (4, 6, 12, 2): {'fn': metal_brushed, 'args': {'base': '#7C8FA0', 'highlight': '#94A3B8', 'shadow': '#5C7080'}},
        # base up (顶部微亮): y=8-10, x=0-12
        (0, 8, 12, 2): {'fn': metal_brushed, 'args': {'base': '#788290', 'highlight': '#A8B0BC', 'shadow': '#505A68'}},
        # unused: y=10-16, 深色填充
        (0, 10, w, 6): {'fn': metal_brushed, 'args': {'base': '#404858', 'highlight': '#505A68', 'shadow': '#333A48'}},
    }
    px = atlas_regions(w, h, regions)
    png(w, h, px, f'{BASE}/block/wind_turbine.png')
    print('wind_turbine.png done')


def gen_geothermal_generator():
    """地热发电机 UV 图集 16×16 — 遵循 §4.2 布局"""
    w, h = 16, 16
    regions = {
        # base_side: y=0-2
        (0, 0, w, 2): {'fn': brick_refractory, 'args': {'brick': '#2D1A0A', 'mortar': '#1A0E05'}},
        # base_up: y=2-4
        (0, 2, w, 2): {'fn': brick_refractory, 'args': {'brick': '#3A2410', 'mortar': '#2D1A0A'}},
        # body_front: y=4-12
        (0, 4, 12, 8): {'fn': metal_brushed, 'args': {'base': '#4A2810', 'highlight': '#5A3215', 'shadow': '#3A1E08', 'noise_pct': 5}},
        # body_up: y=12-14
        (0, 12, w, 2): {'fn': metal_brushed, 'args': {'base': '#5A3215', 'highlight': '#6B3C1A', 'shadow': '#4A2810'}},
        # pipes: y=14-16, 亮橙
        (0, 14, 4, 2): {'fn': metal_brushed, 'args': {'base': '#EA580C', 'highlight': '#FB923C', 'shadow': '#C2410C'}},
        (4, 14, w - 4, 2): {'fn': metal_brushed, 'args': {'base': '#C2410C', 'highlight': '#EA580C', 'shadow': '#9A3412'}},
    }
    px = atlas_regions(w, h, regions)
    png(w, h, px, f'{BASE}/block/geothermal_generator.png')
    print('geothermal_generator.png done')


def gen_solar_panel():
    """太阳能板 UV 图集 16×16"""
    w, h = 16, 16
    regions = {
        # panel up: 蓝色面板 + 网格
        (0, 0, w, 6): {'fn': grid_panel, 'args': {'base': '#1D4ED8', 'grid': '#2563EB', 'cell': 4, 'line': 1}},
        # border (底座侧): y=6-10
        (0, 6, w, 4): {'fn': metal_brushed, 'args': {'base': '#A8B0BC', 'highlight': '#D8DCE4', 'shadow': '#788290'}},
        # base side: y=10-14
        (0, 10, w, 4): {'fn': metal_brushed, 'args': {'base': '#3D3D3D', 'highlight': '#505050', 'shadow': '#2D2D2D'}},
        # base down: y=14-16
        (0, 14, w, 2): {'fn': metal_brushed, 'args': {'base': '#1E1E1E', 'highlight': '#2D2D2D', 'shadow': '#141414'}},
    }
    px = atlas_regions(w, h, regions)
    png(w, h, px, f'{BASE}/block/solar_panel.png')
    print('solar_panel.png done')


def gen_backpack():
    """背包物品 16×16"""
    px = [(0, 0, 0, 0)] * 256
    for y in range(16):
        for x in range(16):
            idx = y * 16 + x
            # 翻盖 (y:0-4)
            if 0 <= y <= 4 and 2 <= x <= 13:
                px[idx] = hex2rgb('#A0781E')
            # 袋身 (y:5-15)
            if 5 <= y <= 15 and 2 <= x <= 13:
                px[idx] = hex2rgb('#8B6914')
            # 缝合线
            if y == 5 and 2 <= x <= 13 and x % 2 == 0:
                px[idx] = hex2rgb('#C4A44A')
            elif y == 5 and 2 <= x <= 13:
                px[idx] = hex2rgb('#4A3510')
            # 搭扣
            if 4 <= y <= 6 and 7 <= x <= 8:
                px[idx] = hex2rgb('#D4AA44')
            # 背带
            if 3 <= y <= 13 and 2 <= x <= 3:
                px[idx] = hex2rgb('#4A3510')
            if 3 <= y <= 13 and 12 <= x <= 13:
                px[idx] = hex2rgb('#4A3510')
            # 前口袋
            if 7 <= y <= 10 and 4 <= x <= 11:
                px[idx] = hex2rgb('#6B4E12')
            if 7 <= y <= 10 and x == 7:
                px[idx] = hex2rgb('#C4A44A')

    # 定向光照：左上角像素加亮（包装物品风格）
    for y in range(16):
        for x in range(16):
            idx = y * 16 + x
            if x <= 1 and y <= 1:
                px[idx] = lighten(px[idx], 10)
            if x >= 14 and y >= 14:
                px[idx] = darken(px[idx], 10)

    png(16, 16, px, f'{BASE}/item/backpack.png')
    print('backpack.png done')


def gen_efficiency_card():
    """效率升级卡 16×16"""
    px = [(0, 0, 0, 0)] * 256
    for y in range(16):
        for x in range(16):
            idx = y * 16 + x
            # 外框 (1px)
            if x == 0 or x == 15 or y == 0 or y == 15:
                px[idx] = hex2rgb('#CA8A04')
            # 内框 (距边 2px)
            elif x == 2 or x == 13 or y == 2 or y == 13:
                px[idx] = hex2rgb('#FDE047')
            # 底色
            elif 1 <= x <= 14 and 1 <= y <= 14:
                px[idx] = hex2rgb('#EAB308')
            # 中心菱形
            cx, cy = 7.5, 7.5
            if abs(x - cx) + abs(y - cy) < 3:
                px[idx] = hex2rgb('#DC2626')
            # 左上光泽
            if x <= 4 and y <= 4:
                px[idx] = hex2rgb('#FEF9C3')
            # 右下暗角
            if x >= 11 and y >= 11:
                px[idx] = hex2rgb('#A16207')

    png(16, 16, px, f'{BASE}/item/efficiency_upgrade.png')
    print('efficiency_upgrade.png done')


def gen_gui(name):
    """GUI 背景 256×256"""
    w, h = 256, 256
    bg = hex2rgb('#C6C6C6')
    border = hex2rgb('#373737')
    inv = hex2rgb('#8B8B8B')
    px = [bg] * (w * h)
    for y in range(h):
        for x in range(w):
            idx = y * w + x
            if x < 4 or x >= 252 or y < 4 or y >= 252:
                px[idx] = border
            elif y >= 172:
                px[idx] = inv
    png(w, h, px, f'{BASE}/gui/{name}_gui.png')
    print(f'{name}_gui.png done')


# ============================================================
# Main
# ============================================================

BASE = 'src/main/resources/assets/solarmod/textures'

gen_wind_turbine()
gen_geothermal_generator()
gen_solar_panel()
gen_backpack()
gen_efficiency_card()
gen_gui('solar_panel')
gen_gui('wind_turbine')
gen_gui('geothermal')

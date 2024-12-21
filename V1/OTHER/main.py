from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
from time import sleep

# 开始
print('/------------------------------------------\\')
print('|          minecraft 0.0.2 模拟器           |')
print('|------------------------------------------|')
print('|  主要程序来源： 网络                        |')
print('|  改进： OOOO                              |')
print('|  主要音频来源： 网络                        |')
print('|  1~4（图片编号）来源： 网络                  |')
print('|  5~6（图片编号）来源： OOOO                 |')
print('|------------------------------------------|')
print('|          minecraft 0.0.2 模拟器           |')
print('\\------------------------------------------/')

# 获取数据
while True:
    try:
        seed = int(input('种子编号：'))
        break
    except ValueError:
        print('请输入数字！')

print('加载所需资源并准备启动中...')

app = Ursina()

# 加载图片文件
grass_texture = load_texture('assets/grass_block.png')
stone_texture = load_texture('assets/stone_block.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture = load_texture('assets/dirt_block.png')
sky_texture = load_texture('assets/skybox.png')
arm_texture = load_texture('assets/arm_texture.png')
tree_stump = load_texture('assets/tree_stump.png')
foliage = load_texture('assets/foliage.png')
punch_sound = Audio('assets/punch_sound', loop=False, autoplay=False)

block_pick = 1

# 关闭FPS显示和关闭按键显示
window.fps_counter.enabled = False
window.exit_button.visible = False

scene.fog_color = color.white
scene.fog_density = 0

def input(key):
    if key == 'q' or key == 'escape':
        quit()

# 定义玩家
player = FirstPersonController()

# 定义常量
CHUNK_SIZE = 4  # 每个块的大小
chunks = {}  # 存储已加载的块
render_distance = 4  # 渲染距离设置为1
MAX_HEIGHT = 8  # 最大高度
MIN_HEIGHT = -4  # 最小高度

# 加载块的函数
def load_chunk(chunk_x, chunk_z):
    if (chunk_x, chunk_z) in chunks:
        return  # 如果块已经加载，直接返回

    print(f"尝试加载块: ({chunk_x}, {chunk_z})")  # 调试信息

    # 生成块
    for z in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            world_x = chunk_x * CHUNK_SIZE + x
            world_z = chunk_z * CHUNK_SIZE + z
            
            # 使用噪声生成高度
            y = floor(noise([world_x / 10, world_z / 10]) * 20)  # 调整缩放因子和高度范围

            # 打印噪声值和计算出的高度
            print(f"噪声值: {noise([world_x / 10, world_z / 10])}, 计算高度: {y}")

            # 检查高度限制
            if y > MAX_HEIGHT:
                print(f"方块 ({world_x}, {y}, {world_z}) 超出最大高度，已删除。")
                continue  # 超出最大高度，跳过生成

            if y < MIN_HEIGHT:
                print(f"方块 ({world_x}, {y}, {world_z}) 超出最小高度，已删除。")
                continue  # 超出最小高度，跳过生成

            # 填充方块
            Block(position=(x, y, z), texture=grass_texture)
            for _y in  range(y - 1, -4, -1):
                Block(position=(x, _y, z), texture=dirt_texture)

    chunks[(chunk_x, chunk_z)] = True  # 标记块为已加载
    print(f"已加载块: ({chunk_x}, {chunk_z})")  # 调试信息

# 卸载块的函数
def unload_chunk(chunk_x, chunk_z):
    if (chunk_x, chunk_z) in chunks:
        del chunks[(chunk_x, chunk_z)]  # 卸载块
        print(f"已卸载块: ({chunk_x}, {chunk_z})")  # 调试信息

# 创建方块的函数
def create_blocks():
    # 生成初始方块
    for z in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            world_x = x
            world_z = z
            
            # 使用噪声生成高度
            y = floor(noise([world_x / 10, world_z / 10]) * 20)  # 调整缩放因子和高度范围

            # 打印噪声值和计算出的高度
            print(f"噪声值: {noise([world_x / 10, world_z / 10])}, 计算高度: {y}")

            # 检查高度限制
            if y > MAX_HEIGHT:
                print(f"方块 ({world_x}, {y}, {world_z}) 超出最大高度，已删除。")
                continue  # 超出最大高度，跳过生成

            if y < MIN_HEIGHT:
                print(f"方块 ({world_x}, {y}, {world_z}) 超出最小高度，已删除。")
                continue  # 超出最小高度，跳过生成

            # 填充方块
            Block(position=(x, y, z), texture=grass_texture)
            for _y in  range(y - 1, -4, -1):
                Block(position=(x, _y, z), texture=dirt_texture)

# 更新
def update():
    global block_pick

    # 检测并切换手持方块
    if held_keys['1']:
        block_pick = 1
        print('当前方块：草方块')
    if held_keys['2']:
        block_pick = 2
        print('当前方块：岩石块')
    if held_keys['3']:
        block_pick = 3
        print('当前方块：木板')
    if held_keys['4']:
        block_pick = 4
        print('当前方块：泥土')
    if held_keys['5']:
        block_pick = 5
        print('当前方块：树桩')
    if held_keys['6']:
        block_pick = 6
        print('当前方块：树叶')

    # 计算当前玩家所在的块
    player_chunk_x = int(player.position.x // CHUNK_SIZE)
    player_chunk_z = int(player.position.z // CHUNK_SIZE)

    # 加载周围的块
    for dz in range(-render_distance, render_distance + 1):
        for dx in range(-render_distance, render_distance + 1):
            load_chunk(player_chunk_x + dx, player_chunk_z + dz)

    # 卸载不在渲染范围内的块
    for (chunk_x, chunk_z) in list(chunks.keys()):
        if abs(chunk_x - player_chunk_x) > render_distance or abs(chunk_z - player_chunk_z) > render_distance:
            unload_chunk(chunk_x, chunk_z)

    # 检测手部按键和运动
    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.active()
    else:
        hand.passive()

    # 如果玩家掉进虚空就传送上来
    if player.position[1] < (-50):
        player.position = Vec3(0, 0.25, 0)

# 定义方块
class Block(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='assets/block',
            origin_y=0.5,
            texture=texture,
            color=color.hsv(0, 0, random.uniform(0.9, 1)),
            scale=0.5,
            collider='box'
        )

    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':
                punch_sound.play()
                if block_pick == 1: Block(position=self.position + mouse.normal, texture=grass_texture)
                if block_pick == 2: Block(position=self.position + mouse.normal, texture=stone_texture)
                if block_pick == 3: Block(position=self.position + mouse.normal, texture=brick_texture)
                if block_pick == 4: Block(position=self.position + mouse.normal, texture=dirt_texture)
                if block_pick == 5: Block(position=self.position + mouse.normal, texture=tree_stump)
                if block_pick == 6: Block(position=self.position + mouse.normal, texture=foliage)
            if key == 'left mouse down':
                punch_sound.play()
                destroy(self)

# 定义天空
class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture=sky_texture,
            scale=150,
            double_sided=True
        )

# 定义手
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='assets/arm',
            texture=arm_texture,
            scale=0.2,
            rotation=Vec3(150, -10, 0),
            position=Vec2(0.4, -0.6)
        )

    def active(self):
        self.position = Vec2(0.3, -0.5)

    def passive(self):
        self.position = Vec2(0.4, -0.6)

##################main##################
noise = PerlinNoise(octaves=3, seed=seed)
scale = 24
print('准备中...')
sleep(1)

print('正在加载地形...')

# 在主程序中调用创建方块的函数
create_blocks()

sky = Sky()
hand = Hand()

app.run()
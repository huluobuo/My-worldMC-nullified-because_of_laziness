from ursina import *  # 导入ursina模块
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise  # 随机地形算法柏林噪声模块
from time import sleep


# 开始
print('/------------------------------------------\\')
print('|          minecraft 1.0.2 模拟器           |')
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
        big = int(input('世界大小：'))
        if big == 0:
            print('世界大小不可为0！')
        else:
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

    # 检测手部按键和运动
    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.active()
    else:
        hand.passive()

    # 如果玩家掉进虚空就传送上来
    if player.position[1] < (-20):
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
            color=color.color(0, 0, random.uniform(0.9, 1)),
            # highlight_color=color.green,
            scale=0.5
        )

    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':
                punch_sound.play()
                if block_pick == 1: block = Block(position=self.position + mouse.normal, texture=grass_texture)
                if block_pick == 2: block = Block(position=self.position + mouse.normal, texture=stone_texture)
                if block_pick == 3: block = Block(position=self.position + mouse.normal, texture=brick_texture)
                if block_pick == 4: block = Block(position=self.position + mouse.normal, texture=dirt_texture)
                if block_pick == 5: block = Block(position=self.position + mouse.normal, texture=tree_stump)
                if block_pick == 6: block = Block(position=self.position + mouse.normal, texture=foliage)
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
finish = 0
# 为某些程序留出一段时间
sleep(1)


print('正在加载地形...')
for z in range(big):
    for x in range(big):
        y = floor(noise([x / scale, z / scale]) * 10)  # 用柏林噪声算法调整方块的x坐标
        block = Block(position=(x, y, z))
        block.y = y

        # 树木 生成概率：1% ?
        if random.randint(1, 100) == 1:
            # 树干
            # 长度范围： 3 ~ 8
            _y = y
            for _high in range(0, random.randint(3, 8), 1):
                _y = _y + 1
                block = Block(position=(x, _y, z), texture=tree_stump)

            # 树叶---有一点单调，但还会更新
            # 就写一个应付过去:)
            _y = _y + 1
            block = Block(position=(x, _y, z), texture=foliage)
            block = Block(position=(x, _y + 1, z), texture=foliage)
            block = Block(position=(x + 1, _y, z - 1), texture=foliage)
            block = Block(position=(x + 1, _y, z), texture=foliage)
            block = Block(position=(x + 1, _y, z + 1), texture=foliage)
            block = Block(position=(x, _y, z - 1), texture=foliage)
            block = Block(position=(x, _y, z + 1), texture=foliage)
            block = Block(position=(x - 1, _y, z - 1), texture=foliage)
            block = Block(position=(x - 1, _y, z), texture=foliage)
            block = Block(position=(x - 1, _y, z + 1), texture=foliage)


        # 修改下方无方块的BUG
        # 设定分界
        _y_ = random.randint(2, 5)
        _y_ = 0 - _y_

        # 泥土层
        for _y in range(_y_, y, 1):
            block = Block(position=(x, _y, z), texture=dirt_texture)

        _y_ = _y_ - 1

        # 岩石层
        for _y in range(-7, _y_, 1):
            block = Block(position=(x, _y, z), texture=stone_texture)


        # 计算打印的图
        pt = '#'
        finish += 1
        _pt = finish / big * 100 / big
        for a in range(0, 50, 1):
            if _pt >= a * 2:
                pt += '>'
            else:
                pt += '-'
        pt += f'#   {_pt}%   已完成：{finish}   总计：{big**2}'

        # 更新上一条加载信息
        print(f'\r{pt}', end='')

print('\n')

sky = Sky()
hand = Hand()

app.run()
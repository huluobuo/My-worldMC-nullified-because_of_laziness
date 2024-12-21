from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
from time import sleep
import tkinter as tk
from tkinter import messagebox
import sys
import os
import logging
from time import time


def setup_logging():
    # 确保日志目录存在
    log_dir = 'V2\\.game\\log'
    os.makedirs(log_dir, exist_ok=True)
    
    # 生成日志文件名：时间-随机数.log
    file_name = str(time())   # 生成时间
    log_file = f'{log_dir}\\{file_name}.log'
    
    # 配置日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )
    return log_file

def start_game(max_height, min_height, chunk_size, render_distance, seed):
    # 设置日志系统
    log_file = setup_logging()
    logging.info('游戏启动')
    logging.info(f'参数: 最大高度={max_height}, 最小高度={min_height}, 区块大小={chunk_size}, 渲染距离={render_distance}, 种子={seed}')
    
    global CHUNK_SIZE, render_distance_global, MAX_HEIGHT, MIN_HEIGHT, sky_texture, arm_texture

    # 设置全局变量
    CHUNK_SIZE = chunk_size
    render_distance_global = render_distance
    MAX_HEIGHT = max_height
    MIN_HEIGHT = min_height
    
    # 开始
    logging.info('正在初始化游戏...')
    print('/------------------------------------------\\')
    print('|          minecraft 0.4.7 模拟器           |')
    print('\\------------------------------------------/')
    print('加载所需资源并准备启动中...')

    try:
        app = Ursina()
        logging.info('Ursina引擎初始化完成')

        # 加载图片文件
        logging.info('正在加载资源文件...')
        try:
            grass_texture = load_texture('.game/assets/grass_block.png')
            stone_texture = load_texture('.game/assets/stone_block.png')
            brick_texture = load_texture('.game/assets/brick_block.png')
            dirt_texture = load_texture('.game/assets/dirt_block.png')
            sky_texture = load_texture('.game/assets/skybox.png')
            arm_texture = load_texture('.game/assets/arm_texture.png')
            tree_stump = load_texture('.game/assets/tree_stump.png')
            foliage = load_texture('.game/assets/foliage.png')
            punch_sound = Audio('.game/assets/punch_sound.wav', loop=False, autoplay=False)
            logging.info('资源文件加载完成')
        except Exception as e:
            logging.error(f'资源加载失败: {str(e)}')
            try:
                punch_sound = Audio(loop=False, autoplay=False)
                logging.warning('使用空音频对象替代')
            except:
                logging.error('无法创建空音频对象')
            raise

        block_pick = 1

        # 关闭FPS显示和关闭按键显示
        window.fps_counter.enabled = False
        window.exit_button.visible = False

        scene.fog_color = color.white
        scene.fog_density = 0

        # 定义玩家
        player = FirstPersonController()
        
        # 注册输入函数
        scene.input = input
        
        # 定义常量
        chunks = {}  # 存储已加载的块

        # 加载块的函数
        def load_chunk(chunk_x, chunk_z):
            if (chunk_x, chunk_z) in chunks:
                logging.info(f"区块已加载: ({chunk_x}, {chunk_z})")
                return  # 如果块已经加载，直接返回

            logging.info(f"正在加载区块: ({chunk_x}, {chunk_z})")

            # 生成
            for z in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    world_x = chunk_x * CHUNK_SIZE + x
                    world_z = chunk_z * CHUNK_SIZE + z
                    y = floor(noise([world_x / scale, world_z / scale]) * 10)

                    # 检查高度限制
                    if y > MAX_HEIGHT:
                        logging.warning(f"方块 ({world_x}, {y + 4}, {world_z}) 超出最大高度，已跳过生成。")
                        continue

                    if y < MIN_HEIGHT:
                        logging.warning(f"方块 ({world_x}, {y + 4}, {world_z}) 超出最小���度，已跳过生成。")
                        continue

                    # 填充方块
                    try:
                        for _y in range(y - 1, -4, -1):
                            Block(position=(world_x, _y + 4, world_z), texture=dirt_texture)
                        Block(position=(world_x, y + 4, world_z), texture=grass_texture)
                    except Exception as e:
                        logging.error(f"在生成方块时发生错误: ({world_x}, {y}, {world_z}), 错误: {str(e)}")

            chunks[(chunk_x, chunk_z)] = True
            logging.info(f"区块加载完成: ({chunk_x}, {chunk_z})")

        # 卸载块的函数
        def unload_chunk(chunk_x, chunk_z):
            if (chunk_x, chunk_z) in chunks:
                del chunks[(chunk_x, chunk_z)]
                logging.info(f"已卸载区块: ({chunk_x}, {chunk_z})")

        # 创建方块的函数
        def create_blocks():
            # 生成初始方块
            for z in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    world_x = x
                    world_z = z
                    y = floor(noise([world_x / scale, world_z / scale]) * 10)

                    # 检查高度限制
                    if y > MAX_HEIGHT:
                        print(f"方块 ({world_x}, {y}, {world_z}) 超出最大高度，已删除。")
                        continue  # 超出最大高度，跳过生成

                    if y < MIN_HEIGHT:
                        print(f"方块 ({world_x}, {y}, {world_z}) 超出最小高度，已删除。")
                        continue  # 超出最小高度，跳过生成

                    # 填充方块
                    Block(position=(world_x, y, world_z), texture=grass_texture)
                    for _y in range(y - 1, -4, -1):
                        Block(position=(world_x, _y + 4, world_z), texture=dirt_texture)

        # 更新
        def update():
            # 在运行时输出是否被调用
            logging.info('update() 被调用')
            
            # 全局变量
            global block_pick
            try:
                # 检测并切换手持方块
                if held_keys['1']:
                    block_pick = 1
                    logging.info('切换到草方块')
                if held_keys['2']:
                    block_pick = 2
                    logging.info('切换到岩石块')
                if held_keys['3']:
                    block_pick = 3
                    logging.info('切换到木板')
                if held_keys['4']:
                    block_pick = 4
                    logging.info('切换到泥土')
                if held_keys['5']:
                    block_pick = 5
                    logging.info('切换到树桩')
                if held_keys['6']:
                    block_pick = 6
                    logging.info('切换到树叶')

                # 获取玩家当前位置和区块
                current_pos = player.position
                current_chunk_x = int(current_pos.x // CHUNK_SIZE)
                current_chunk_z = int(current_pos.z // CHUNK_SIZE)
                
                # 检查玩家是否进入新区块
                if not (current_chunk_x, current_chunk_z) in chunks:
                    logging.warning(f'玩家进入未加载区块: ({current_chunk_x}, {current_chunk_z})')
                    logging.info(f'玩家当前位置: x={current_pos.x:.2f}, y={current_pos.y:.2f}, z={current_pos.z:.2f}')

                # 加载周围的区块
                for dz in range(-render_distance_global, render_distance_global + 1):
                    for dx in range(-render_distance_global, render_distance_global + 1):
                        try:
                            load_chunk(current_chunk_x + dx, current_chunk_z + dz)
                        except Exception as e:
                            logging.error(f'加载区块失败: ({current_chunk_x + dx}, {current_chunk_z + dz}), 错误: {str(e)}')

                # 卸载远处的区块
                for chunk_x, chunk_z in list(chunks.keys()):
                    if abs(chunk_x - current_chunk_x) > render_distance_global or \
                       abs(chunk_z - current_chunk_z) > render_distance_global:
                        unload_chunk(chunk_x, chunk_z)

                # 虚空检测
                if current_pos.y < -25:
                    logging.warning(f'玩家掉入虚空，从位置 ({current_pos.x:.2f}, {current_pos.y:.2f}, {current_pos.z:.2f}) 传送至初始位置')
                    player.position = Vec3(0, 32, 0)
                    player.velocity = Vec3(0, 0, 0)  # 重置速度 防止掉落至远处

            except Exception as e:
                logging.error(f'更新循环中发生错误: {str(e)}')

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

        ##################main##################
        noise = PerlinNoise(octaves=3, seed=seed)
        scale = 24
        logging.info('准备中...')
        sleep(1)

        logging.info('正在加载地形...')

        # 在主程序中调用创建方块的函数
        create_blocks()

        # 正确注册更新函数
        app.update = update()  # 确保 update 函数被注册为持续调用 <------------------------------|                 我****************************************
        #                                                                                      |                   ****************************************
        #########################################################                              |                   ****************************************
        #          天灵灵，地灵灵，太上老君快显灵！！！            #------------------------------|
        #          求求了，别出错，不然我得重新写！！！            #
        #          好好运行，谢谢！！！！！！！！！！！            #    
        #########################################################
        #                                                       #
        #                 ---我为你烧香---                       #
        #                                                       #
        #-------------------------------------------------------#
        #                                                       # 
        #       /-\            /-\           /-\                #
        #       \_/            \_/           \_/                #
        #        |              |             |                 #
        #        |              |             |                 #
        #-------------------------------------------------------#
        # 注：
        # 我不知道为什么update函数不能被正确使用
        # 我尝试了很多方法，但是都没有成功
        # 我现在正在使用Windows 11系统，Python 3.10.11版本
        # 如果你能帮我解决这个问题，请给我发送邮件，请说明解决方法
        # 我会非常感激你的帮助
        # 谢谢！
        # ！！！！！！！！！！！！！！


        logging.info('游戏启动完成，开始运行')
        app.run()

    except Exception as e:
        logging.critical(f'游戏运行时发生严重错误: {str(e)}')
        raise

def main():
    try:
        # 检查命令行参数
        if len(sys.argv) == 6:
            logging.info('使用命令行参数启动游戏')
            max_height = int(sys.argv[1])
            min_height = int(sys.argv[2])
            chunk_size = int(sys.argv[3])
            render_distance = int(sys.argv[4])
            seed = int(sys.argv[5])
            start_game(max_height, min_height, chunk_size, render_distance, seed)
        else:
            logging.info('启动图形界面')
            root = tk.Tk()
            root.title("Minecraft 启动器")
            root.geometry("300x250")

            # 设置字体和颜色
            font_style = ('Arial', 12)
            bg_color = '#f0f0f0'
            root.configure(bg=bg_color)

            # 创建输入框和标签
            tk.Label(root, text="最大高度:", bg=bg_color, font=font_style).grid(row=0, column=0, padx=10, pady=5)
            max_height_entry = tk.Entry(root)
            max_height_entry.grid(row=0, column=1, padx=10, pady=5)
            max_height_entry.insert(0, "16")

            tk.Label(root, text="最小高度:", bg=bg_color, font=font_style).grid(row=1, column=0, padx=10, pady=5)
            min_height_entry = tk.Entry(root)
            min_height_entry.grid(row=1, column=1, padx=10, pady=5)
            min_height_entry.insert(0, "-4")

            tk.Label(root, text="区块大小:", bg=bg_color, font=font_style).grid(row=2, column=0, padx=10, pady=5)
            chunk_size_entry = tk.Entry(root)
            chunk_size_entry.grid(row=2, column=1, padx=10, pady=5)
            chunk_size_entry.insert(0, "4")

            tk.Label(root, text="渲染距离:", bg=bg_color, font=font_style).grid(row=3, column=0, padx=10, pady=5)
            render_distance_entry = tk.Entry(root)
            render_distance_entry.grid(row=3, column=1, padx=10, pady=5)
            render_distance_entry.insert(0, "1")

            tk.Label(root, text="种子:", bg=bg_color, font=font_style).grid(row=4, column=0, padx=10, pady=5)
            seed_entry = tk.Entry(root)
            seed_entry.grid(row=4, column=1, padx=10, pady=5)
            seed_entry.insert(0, "0")

            def launch_game():
                try:
                    max_height = int(max_height_entry.get())
                    min_height = int(min_height_entry.get())
                    chunk_size = int(chunk_size_entry.get())
                    render_distance = int(render_distance_entry.get())
                    seed = int(seed_entry.get())
                    
                    logging.info('从启动器界面启动游戏')
                    root.destroy()
                    start_game(max_height, min_height, chunk_size, render_distance, seed)
                    
                except ValueError:
                    logging.error('启动器输入值无效')
                    messagebox.showerror("输入错误", "请确保所有输入都是有效的数字。")

            # 启动按钮
            start_button = tk.Button(root, text="启动游戏", command=launch_game, bg='#4CAF50', fg='white', font=font_style)
            start_button.grid(row=5, columnspan=2, pady=15)

            root.mainloop()

    except Exception as e:
        logging.critical(f'程序启动失败: {str(e)}')
        raise

if __name__ == "__main__":
    setup_logging()  # 初始化日志系统
    logging.info('程序启动')
    main()
import json
import os
import time


def _check_and_load_file():
    print("正在检查必要的文件...")
    # 首先检查文件是否存在
    if not os.path.exists('version.json'):
        print("-ERROR-  >  必要的文件不存在")
        exit()

    with open('version.json', 'r', encoding='utf-8') as f:
        # 先读取文件内容
        content = f.read()

    print("检查完毕")
    print("正在准备启动...")
    # 尝试解析JSON
    data = json.loads(content)
    # 获取当前路径
    where = os.path.abspath('.')
    print("正在启动...")
    return data, where



def start_mc(data, where):
    print("正在检查并安装所需文件...")
    file_list = data[1].split("+-+")
    for i in file_list:
        print("正在检查或安装 " + i + "   ---   pip: " + where + "\\python310\\python.exe -m pip install " + i)
        os.system(where + "\\python310\\python.exe -m pip install " + i)                                   #我的电脑就这样，如果你们电脑不一样，请自行修改
    
    print("正在启动游戏...")
    time.sleep(1)
    
    print(data[2])
    if data[2]:
        file = ".\\" + data[3] + "\\help.txt"
        with open(file, "w", encoding="utf-8") as f:
            f.write(where + "\\python310\\python.exe")    #python路径
        cmd = f"{where}\\python310\\python.exe {where}{data[0]}"
    else:
        cmd = f"{where}\\python310\\python.exe {where}{data[0]}"
    
    os.system(cmd)



def _start_game(data, where):
    print("/-----------------------------------\\")
    print("|             我的世界               |")
    print("|              启动器                |")
    print("\\-----------------------------------/")

    print("以下载的游戏列表：")                                # 不是，也太简陋了吧
    for version_name in data:
        if isinstance(data[version_name], list):
            print(f"\t{version_name}  --->  主文件：{data[version_name][0]}, 依赖项：{data[version_name][1]}")
        else:
            print(f"\t{version_name}  --->  {data[version_name]}")

    _help_list_1 = ["1. 启动游戏",  "2. 下载游戏", "3. 退出"]
    print("请选择操作：")
    for i in _help_list_1:
        print("\t" + i)

    answer = input("请输入序号：")

    if answer == "1":
        answer = input("请输入游戏版本：")
        start_mc(data[answer], where)
    elif answer == "2":
        print("正在下载游戏...")
    elif answer == "3":
        print("正在退出...")
        time.sleep(1)
        exit()
    else:
        print("-ERROR-  >  输入错误")


def main():
    data, where = _check_and_load_file()

    print(data, where)
    _start_game(data, where)

if __name__ == "__main__":
    main()

import datetime
import pathlib
import pickle
import random

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

from tools.utils import get_history_data

data_type_dict_str = {
    '1': '累积确诊人数',
    '2': '现存确诊人数',
    '3': '累积死亡人数',
    '4': '累积治愈人数',
}

data_type_dict = {
    '1': 'confirmedCount',
    '2': 'currentConfirmedCount',
    '3': 'deadCount',
    '4': 'curedCount',
}

# 默认展示key=1的数据
_default_type = '1'
# 默认显示top 10
_default_num = 10
# top n 的最小值
_min_num = 1
# top n 的最大值
_max_num = 40

# 用来给每一个国家分配一个颜色值
def generate_country_colors(countries):

    # 文件名
    file_name = './country_color_map'
    _path = pathlib.Path(file_name)
    # 判断本地是否已经存在 file_name 文件
    if not _path.exists():
        # 国家名称去重
        country_names = set(countries)
        # 使用 matplotlib 中的 颜色值来进行分配
        colors = list(mpl.colors.XKCD_COLORS.values())
        # 打乱colors排序
        random.shuffle(colors)
        # 从颜色值集合中取出 传入国家数量的颜色值
        country_colors = colors[:len(country_names)]
        # 创建国家与颜值值的对应关系
        country_color_map =dict(zip(country_names, country_colors))

        # 将对应关系数据保存到文件
        with open(_path.absolute(), 'wb') as f:
            pickle.dump(country_color_map, f)
    else:
        # 表示本地已经有对应关系数据,读取数据
        with open(_path.absolute(), 'rb') as f:
            country_color_map = pickle.load(f)



    return country_color_map

# 主函数，入口
def handle_data_draw_chart(t, num):
    # 第一步，加载历史疫情数据
    # 通过pandas.read_json()
    # datas = pd.read_json('../spider/datas/all_countris_datas.json')
    datas = get_history_data()
    # print(datas)

    # 第二步，得到要展示的数据， 先只对累积确诊人数 进行展示 即 confirmedCount
    # 得到的数据格式：每一行包括所有国家当日累积确诊人数
    pivot_table_data = pd.pivot_table(data=datas, index=['dateId'], values=data_type_dict.get(t), columns='country_name', fill_value=0)
    # print(pivot_table_data)
    # 查看有多少个国家数据 总共有215个国家或地区数据
    # print(pivot_table_data.columns)

    # 第三步，需要给每一个国家分配一个颜色
    country_colors = generate_country_colors(pivot_table_data.columns)
    # print(country_colors)

    # 第四步， 创建画布
    # fig表示一个画布， ax表示为子图
    fig, ax = plt.subplots(figsize=(16, 9))

    plt.box(False)
    # 用来设置x轴刻度数字格式
    xf = mticker.StrMethodFormatter('{x:,.0f}')

    # 内部函数，用来负责具体的图形绘制
    # 以天为单位进行绘制
    def _draw_barh_chart(day):
        # 需要清理上一次绘制的图形,得到一个干净的画板
        ax.clear()

        # 根据传入的day 日期，从透视表中取出这一天的所有国家的累积确诊人数的数据
        # 对数据进行降序排序
        # 取出top n
        day_datas = pivot_table_data.loc[day].sort_values(ascending=False).head(num).sort_values()
        # print(day_datas)
        # 通过top n 个国家的名称，取到它们对应的颜值值
        day_country_colors = [country_colors[name] for name in day_datas.index]

        # 在ax中绘制图形
        ax.barh(day_datas.index, day_datas.values, color=day_country_colors)

        # 显示出累积确诊人数数字
        for i, value in enumerate(day_datas.values):
            ax.text(value, i, f'{value:,.0f}', ha='left', va='center', size=14, color=day_country_colors[i])

        # 设置网络线的样式
        ax.grid(which='major', axis='x', linestyle='-.')
        # 把x轴刻度数字放到图的顶部
        ax.xaxis.set_ticks_position('top')
        # 设置x轴刻度数字的显示格式
        ax.xaxis.set_major_formatter(xf)

        # 设置标题
        ax.set_title(f'Top {num} 国家{data_type_dict_str.get(t)}', fontsize = 25, color='black')

        # 显示日期
        str2date = datetime.datetime.strptime(str(day), '%Y%m%d') # 将 day 转换为 datetime 格式
        date2str = str2date.strftime('%Y-%m-%d')
        ax.text(0.9, 0.2, date2str, transform=ax.transAxes, size=30, color='red', ha='right')

    # _draw_barh_chart(20201201)
    ani = mpl.animation.FuncAnimation(fig, _draw_barh_chart, frames=pivot_table_data.index, repeat=False, interval=50)

    # 第一个输出格式：mp4
    # 注意事项：
    #需要安装ffmpeg http://ffmpeg.org/download.html
    """
    在windows系统下：
    ffmpegpath = os.path.abspath("./ffmpeg/bin/ffmpeg.exe")
    matplotlib.rcParams["animation.ffmpeg_path"] = ffmpegpath
    writer = animation.FFMpegWriter()
    anim.save(fname,writer = writer)
    """
    # writer = mpl.animation.FFMpegWriter()
    # ani.save('barh.mp4', writer=writer)

    # 第二种输出格式: GIF
    #注意事项：
    # 需要安装imagemagick https://imagemagick.org/script/download.php
    # mac 上可以通过 brew install imagemagick
    # ani.save('barh.gif', writer='imagemagick')

    plt.show()


# 获取用户输入
def input_data():
    t, num = _default_type, _default_num
    # 获取用户选择哪个数据点进行展示
    while True:
        print(f'请选择展示哪个数据:(默认为:{data_type_dict_str.get(_default_type)})')
        print('1. 累积确诊人数')
        print('2. 现存确诊人数')
        print('3. 累积死亡人数')
        print('4. 累积治愈人数')
        # 获取用户的输入
        input_type = input()
        if data_type_dict_str.get(input_type):
            t = input_type
            break
        elif input_type == '':
            break
    # 获取用户选择top 多少进行显示
    while True:
        print(f'请输入要展示TOP多少个国家的数据（{_min_num}～{_max_num}）:(默认为:{_default_num})')
        input_num = input()
        if input_num.isdigit() and _min_num <= int(input_num) <= _max_num:
            num = int(input_num)
            break
        elif input_num == '':
            break
    return (t, num)

if __name__ == "__main__":
    t, num = input_data()
    handle_data_draw_chart(t, num)


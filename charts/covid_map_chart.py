import datetime
import pathlib
import pickle

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import rgb2hex

from tools.utils import handle_different_country_name, init_geom_infos


# 入口函数
def draw_covid_map_chart():
    # 加载历史疫情数据
    datas = pd.read_json('../spider/datas/all_countris_datas.json')
    # print(datas.columns)
    #创建透视表
    pivot_table_data = datas.pivot_table(values='confirmedCount', index='dateId', columns='country_name', fill_value=0)
    print(pivot_table_data.index)

    # 世界地图绘制的投影方式
    proj = ccrs.PlateCarree()

    # 创建画布，
    fig, ax = plt.subplots(figsize=(16,9), subplot_kw={'projection': proj})
    # 绘制海岸线
    # ax.coastlines()

    vmax = 10_000
    # 调色板
    cmap = plt.cm.YlOrRd
    # 各个国家的轮廓线颜色
    edgecolor = 'black'


    #初始化世界地图数据（所有地理位置信息）
    country_geom_dict = init_geom_infos()

    # 两系统中国家中文名称不一致的对应关系
    diffrent_country_names_dict = handle_different_country_name()

    # 疫情数据中的所有国家信息
    pivot_contries = set(pivot_table_data.columns)

    def _draw_one_day_map_chart(day):
        ax.clear()

        # 根据日期获取数据
        day_datas = pivot_table_data.loc[day]

        # 通过循环世界地理信息来绘制地图
        for name, geom in country_geom_dict.items():
            # 统一疫情数据和地理位置中的国家名称，
            # 如果不同的字典里没有，就表示两地的国家名称是一致的。
            country_name = diffrent_country_names_dict.get(name) or name

            if country_name in pivot_contries:
                # 表示地理信息中的国家有疫情数据
                value = day_datas[country_name]

                # 通过疫情数据的大小，来判断这个国家或地区在世界地图上，应该填充什么颜色
                # 获得一个颜色值的元组(r,g,b,a)
                c = cmap(np.sqrt(value / vmax))
                # 将元组数据转换成16进制的颜色值，如：#f382ab
                # 填充国家的颜色值
                fill_color = rgb2hex(c)
                ax.add_geometries([geom], proj, facecolor=fill_color, edgecolor=edgecolor)

            else:
                # 表示地理信息中的国家或者地区没有在疫情数据中
                c = cmap(0)
                fill_color = rgb2hex(c)
                ax.add_geometries([geom], proj, facecolor=fill_color, edgecolor=edgecolor)


        #显示日期
        str2date = datetime.datetime.strptime(str(day), '%Y%m%d')
        date2str = str2date.strftime('%Y-%m-%d')
        ax.set_title(f'全球疫情变化情况{date2str}', fontsize=25, color='red')

        # 统计 day 这一天的全球累积确诊人数
        total_count = day_datas.sum()
        fig.suptitle(f'全球累积确诊人数:{total_count:,.0f}', verticalalignment='bottom', y=0.1, fontsize=27, color='red')


    # 在右侧添加一个颜色刻度条 add_axes([left, bottom, width, height])
    cax = fig.add_axes([0.92, 0.2, 0.02, 0.6])
    # 颜色条
    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
    # 放在右侧的一个颜色板
    mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm)

    # ax.set_title('全球最新疫情数据', fontsize=25, color='red')

    ani = mpl.animation.FuncAnimation(fig, _draw_one_day_map_chart, frames=pivot_table_data.index, repeat=False, interval=50)

    plt.show()


if __name__ == "__main__":
    draw_covid_map_chart()

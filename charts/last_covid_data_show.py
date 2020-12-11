import pathlib
import pickle

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import rgb2hex

from tools.utils import handle_different_country_name, init_geom_infos, get_last_updated_data


# 入口函数
def draw_last_covid_map_chart():
    # 加载最新疫情数据
    # last_datas = pd.read_json('../spider/datas/last_updated_dxy_datas.json')
    last_datas = get_last_updated_data()
    # print(last_datas.columns)
    #创建透视表
    pivot_table_data = last_datas.pivot_table(values='confirmedCount', index='provinceName', fill_value=0)
    # print(pivot_table_data)

    # 世界地图绘制的投影方式
    proj = ccrs.PlateCarree()

    # 创建画布，
    fig, ax = plt.subplots(figsize=(16,9), subplot_kw={'projection': proj})
    # 绘制海岸线
    ax.coastlines()

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
    pivot_contries = set(pivot_table_data.index)

    # 通过循环世界地理信息来绘制地图
    for name, geom in country_geom_dict.items():
        # 统一疫情数据和地理位置中的国家名称，
        # 如果不同的字典里没有，就表示两地的国家名称是一致的。
        country_name = diffrent_country_names_dict.get(name) or name

        if country_name in pivot_contries:
            # 表示地理信息中的国家有疫情数据
            value = pivot_table_data.loc[country_name]['confirmedCount']

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

    # 在右侧添加一个颜色刻度条 add_axes([left, bottom, width, height])
    cax = fig.add_axes([0.92, 0.2, 0.02, 0.6])
    # 颜色条
    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
    # 放在右侧的一个颜色板
    mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm)

    ax.set_title('全球最新疫情数据', fontsize=25, color='red')

    plt.show()


if __name__ == "__main__":
    draw_last_covid_map_chart()

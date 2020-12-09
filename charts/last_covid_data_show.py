import pathlib
import pickle

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import rgb2hex


# 处理dxy.cn网站上的国家中文名称与 使用的地理信息文件中的国家中文名称不一致的问题。
def handle_different_country_name():
    """
    key 为 地理信息中的国家名称
    value 为 dxy.cn网站上的国家中文名称
    """
    countries_name_dict = {'中华人民共和国': '中国', '中非共和國': '中非共和国', '蘇利南': '苏里南',
        '迦納': '加纳', '幾內亞比索': '几内亚比绍', '赞比亚': '赞比亚共和国', '波札那': '博茨瓦纳', '亞美尼亞': '亚美尼亚',
        '刚果民主共和国': '刚果（金）', '刚果共和国': '刚果（布）', '馬其頓共和國': '北马其顿', '羅馬尼亞': '罗马尼亚',
        '荷属圣马丁': '圣马丁岛', '賽普勒斯': '塞浦路斯', '多明尼加': '多米尼加', '委內瑞拉': '委内瑞拉', '马里共和国': '马里',
        '奈及利亞': '尼日利亚', '大韩民国': '韩国', '蒲隆地': '布隆迪共和国', '蒙特內哥羅': '黑山', '蒙古国': '蒙古',
        '荷蘭': '荷兰', '苏丹共和国': '苏丹', '斐濟': '斐济', '突尼西亞': '突尼斯', '白罗斯': '白俄罗斯', '玻利維亞': '玻利维亚',
        '爱尔兰共和国': '爱尔兰', '辛巴威': '津巴布韦', '拉脫維亞': '拉脱维亚', '波斯尼亚和黑塞哥维那': '波黑',
        '新喀里多尼亞': '新喀里多尼亚', '斯里蘭卡': '斯里兰卡', '也门': '也门共和国', '阿拉伯联合酋长国': '阿联酋'
     }
    return countries_name_dict

# 获取国家地理信息
def init_geom_infos():

    _path = pathlib.Path('./country_geom_info')
    if not _path.exists():
        # 获取国家地理 shapefile文件，它返回的是文件的路径url,如果本地没有缓存，会先从网上下载
        # https://github.com/nvkelso/natural-earth-vector/tree/master/zips
        shp_file = shpreader.natural_earth(resolution='50m', category='cultural', name='admin_0_countries')
        # 创建一个地理信息文件阅读器
        reader = shpreader.Reader(shp_file)
        # 通过阅读器获取国家地理信息
        countries_geom_map = reader.records()

        # 用来存入国家与地理位置信息的对应关系
        country_geom_dict = {}

        # 得到国家中文名与地理信息的对应关系
        for c in countries_geom_map:
            country_geom_dict[c.attributes['NAME_ZH']] = c.geometry

        with open(_path.absolute(), 'wb') as f:
            pickle.dump(country_geom_dict, f)

    else:
        with open(_path.absolute(), 'rb') as f:
            country_geom_dict = pickle.load(f)

    return country_geom_dict

# 入口函数
def draw_last_covid_map_chart():
    # 加载最新疫情数据
    last_datas = pd.read_json('../spider/datas/last_updated_dxy_datas.json')
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

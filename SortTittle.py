# 有问题提交Issue https://github.com/WadeChenn/Plex-SortTittle
# 或联系 yerwer@foxmail.com
# 库名参数-l (库名或 all ) -n (库编号) -c (是否覆盖 1 or 0) -log(1 or 0 是否打开进度条log)
#########################参数初始化(使用配置文件请修改此处)############################
USE_INIT=False                               #使用当前配置请设为True,否则将尝试从外部获取参数
PLEX_TOKEN="zZzxxxxxxxJssiw2zcy"           #Plextoken获取,具体方法请自行查找 "zZzxxxxxxxJssiw2zcy" *必须设置
PLEX_URL="http://plex.xxx.cn:32400"         #Plexurl "http://plex.xxx.cn:32400" *必须设置
RECOVER=False                               #是否覆盖已有的拼音排序
LIB_NAME=''                                 #要排序的库名(存在时库编号不生效)
LIB_NUMBER=6                                #要排序的库编号(不使用库编号则设为0)
ENABLE_LOG=1                                #是否输出进度条
##############################################################

import os
from importlib import import_module
from pickle import FALSE, TRUE
import sys

#########################依赖库初始化###########################
# 依赖库列表
import_list=[
    'pypinyin',
    'plexapi',
    'argparse'
]
# 判断依赖库是否安装,未安装则安装对应依赖库
sourcestr = "https://pypi.tuna.tsinghua.edu.cn/simple/"  # 镜像源
def GetPackage(PackageName):
    comand = "pip install " + PackageName +" -i "+sourcestr
    # 正在安装
    print("------------------正在安装" + str(PackageName) + " ----------------------")
    print(comand + "\n")
    os.system(comand)
for v in import_list:
    try:
        import_module(v)
    except ImportError:
        print("Not find "+v+" now install")
        GetPackage(v)
##############################################################

import pypinyin
from plexapi.server import PlexServer
import re
import argparse




def uniqify(seq):
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()


def check_contain_chinese(check_str):  # Judge chinese
    for ch in check_str:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def chinese2pinyin(chinesestr): #chinese to pyinyin
    pyinyin_list = []
    pinyin = pypinyin.pinyin(chinesestr, style=pypinyin.FIRST_LETTER)
    for i in range(len(pinyin)):
        pyinyin_list.append(str(pinyin[i][0]).upper())
    pyinyin_str = ''.join(pyinyin_list)
    return pyinyin_str

def removePunctuation(query):
    # 去除标点符号（只留字母、数字、中文)
    if query:
        rule = re.compile(u"[^a-zA-Z0-9]")
        query = rule.sub('', query)
    return query

def loopThroughAllMovies(videos):
    print("正在进行索引请稍候...")
    video_len=len(videos.all())
    for video,i in zip(videos.all(),range(video_len)):
        j=int(i/video_len*100)
        if i==video_len-1:
            j=100
        if ENABLE_LOG:
            print("\r", end="")
            print("进度: {}%: ".format(j), "▓" * (j // 2)," " * (50-j // 2), end=str(i+1)+"/"+str(video_len))
            sys.stdout.flush()
        title = video.title
        if video.titleSort:  # 判断是否已经有标题
            con = video.titleSort
            if (check_contain_chinese(con) or RECOVER):
                SortTitle = chinese2pinyin(title)
                SortTitle=removePunctuation(SortTitle)
                try:
                    video.editSortTitle(SortTitle)
                except:
                    print("Edit SortTitle error")
            #     continue
            # continue




if __name__ == '__main__':

    parse_xls = argparse.ArgumentParser(description="parse arguement of SortTittle")
    parse_xls.add_argument('-url', nargs='?', default=None)
    parse_xls.add_argument('-token', nargs='?', default=None)
    parse_xls.add_argument('-c', nargs='?', default=0)
    parse_xls.add_argument('-n', nargs='?', default=0)
    parse_xls.add_argument('-l', nargs='?', default='')
    parse_xls.add_argument('-log', nargs='?', default=1)

    #get param
    if USE_INIT==False:
        parse_argument = parse_xls.parse_args()
        # PLEX_URL=parse_argument.url
        # PLEX_TOKEN=parse_argument.token
        RECOVER=parse_argument.c
        LIB_NAME=parse_argument.l
        LIB_NUMBER=parse_argument.n
        ENABLE_LOG=parse_argument.log

    if ENABLE_LOG:
        print("--------------------------------------")
        print("正在连接PLEX服务器...")
        print("PLEX_URL = "+PLEX_URL)
        print("PLEX_TOKEN = "+PLEX_TOKEN)
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    except:
        print("plex url 或 token错误!")
        os._exit()
    if ENABLE_LOG:
        print("服务器连接成功")
        print("--------------------------------------")
        print("Start Serching!")
        print("--------------------------------------")
    libtable=[]
    for section in plex.library.sections():
        # if section.type == 'show' or section.type =='movie':
        print(section.title,section.key)
        # print(section.collections.title)

        libtable.append(section.title)
    # for collection in plex.library.collections():
        # print(collection.title,collection.key)
        # libtable.append(section.title)
    print("--------------------------------------")
    if len(LIB_NAME)>0:
        if LIB_NAME =="all":
            print("All libs Start!")
            # loopThroughAllMovies(plex.library)
            # print("\n排序成功!")
            for i in range(len(libtable)):
                print("\nStart NO."+str(i)+" "+libtable[i])
                videos = plex.library.section(libtable[i])
                loopThroughAllMovies(videos)
            print("\n排序成功!")
        else:
            print("指定库为:"+LIB_NAME+" Start!")
            try:
                videos = plex.library.section(LIB_NAME)
                loopThroughAllMovies(videos)
                print("\n排序成功!")
            except:
                print("库名错误!")

    else:
        if LIB_NUMBER != 0:
            try:
                videos = plex.library.sectionByID(int(LIB_NUMBER))
                loopThroughAllMovies(videos)
                print("\n排序成功!")
            except:
                print("出错!")
                os._exit()
        else:
            print("未设定库名")
            LIB_NUMBER = input('请输入你要排序的库编号：')
            LIB_NUMBER=int(LIB_NUMBER)
            try:
                videos = plex.library.sectionByID(LIB_NUMBER)
                loopThroughAllMovies(videos)
                print("\n排序成功!")
            except:
                print("出错!")
                os._exit()


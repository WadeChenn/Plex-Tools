#!/usr/bin/env python3
# 有问题提交Issue https://github.com/WadeChenn/Plex-SortTittle
# 或联系 yerwer@foxmail.com █
# 库名参数-l (库名或 all ) -n (库编号) -c (是否覆盖 1 or 0) -log(1 or 0 是否打开进度条log)
# 库编号 -n {section_id}  媒体编号 -mid {rating_key}  歌手编号-mid {grandparent_rating_key}
from config import *
##############################################################
import os
from importlib import import_module
from pickle import FALSE, TRUE
import sys
import urllib

#########################依赖库初始化###########################
# 依赖库列表
import_list=[
    'plexapi',
    'qbittorrentapi',
    'argparse'
]

# 判断依赖库是否安装,未安装则安装对应依赖库
sourcestr = "https://pypi.tuna.tsinghua.edu.cn/simple/"  # 镜像源
def GetPackage(PackageName):
    comand = "pip install " + PackageName  +" -i "+sourcestr
    # 正在安装
    print("------------------正在安装" + str(PackageName) + " ----------------------")
    print(comand + "\n")
    os.system(comand)
for v in import_list:
    if v=='qbittorrentapi':
        try:
            import_module(v)
        except ImportError:
            print("Not find "+v+" now install")
            GetPackage('qbittorrent-api')
    else:
        try:
            import_module(v)
        except ImportError:
            print("Not find "+v+" now install")
            GetPackage(v)
##############################################################

from plexapi.server import PlexServer
import re
import qbittorrentapi
import argparse
if __name__ == '__main__':
    needlimit=False
    ineraddress={"127","10","192"}
    # instantiate a Client using the appropriate WebUI configuration
    qbt_client = qbittorrentapi.Client(
        host=QBIT_URL,
        port=QBIT_PORT,
        username=QBIT_MAME,
        password=QBIT_PASSWORD,
    )
    # the Client will automatically acquire/maintain a logged-in state
    # in line with any request. therefore, this is not strictly necessary;
    # however, you may want to test the provided login credentials.
    try:
        qbt_client.auth_log_in()
        print('Qbit登入成功')
    except qbittorrentapi.LoginFailed as e:
        print(e)
        print("qbit 登入失败!")

    parse_xls = argparse.ArgumentParser(description="parse arguement of qbit control")
    parse_xls.add_argument('-s', nargs='?', default=0)


    #get param
    parse_argument = parse_xls.parse_args()
    if parse_argument.s!=0:
        SPEEDLIMIT=parse_argument.s*1000
    else:
        SPEEDLIMIT=SPEEDLIMIT*1000

    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    except Exception as e:
        print(e)
        print("plex url 或 token错误!")
        os._exit()
    sessions = plex.sessions()
    for session in sessions:
        for player in session.players:
            address=player.address.split('.')[0]
            if address not in ineraddress:
                needlimit=True

    # COMMAND="test"
    if needlimit:
        print("Sessions active ({count}).".format(count=len(sessions)))
        qbt_client.transfer_set_upload_limit(limit=SPEEDLIMIT)
    else:
        print("No active sessions.")
        # print("Executing command: {cmd}".format(cmd=COMMAND))
        qbt_client.transfer_set_upload_limit(limit=102400000)


   
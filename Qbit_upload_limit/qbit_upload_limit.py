#!/usr/bin/env python3
# 有问题提交Issue https://github.com/WadeChenn/Plex-SortTittle
# 或联系 yerwer@foxmail.com █
# 配合Tautulli使用,在开始,暂停,恢复,停止时触发脚本即可 无需参数传入
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
        print('Qbit 登入成功')
    except qbittorrentapi.LoginFailed as e:
        print(e)
        print("Qbit 登入失败!")

    parse_xls = argparse.ArgumentParser(description="parse arguement of qbit control")
    parse_xls.add_argument('-s', nargs='?', default=0)


    #get param
    parse_argument = parse_xls.parse_args()
    if parse_argument.s!=0:
        SPEEDLIMIT=parse_argument.s*1024
    else:
        SPEEDLIMIT=SPEEDLIMIT*1024

    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    except Exception as e:
        print(e)
        print("plex url 或 token错误!")
        os._exit()
    sessions = plex.sessions()
    bandwidth=0
    for session in sessions:
        if session.TYPE=='track':
            continue
        for player in session.players:
            address=player.address.split('.')[0]
            if address not in ineraddress and player.state!='paused':
                bandwidth=bandwidth+session.sessions[0].bandwidth/1024/8
                needlimit=True
    SPEEDLIMIT=(NET_BANDWIDTH-bandwidth)*1024*1024
    # COMMAND="test"
    if needlimit:
        print("有 ( {count} ) 个设备正在活动，其中含有外网正在播放的设备，Qbit开始限速,速度为{speedlimit}m/s".format(count=len(sessions),speedlimit=SPEEDLIMIT/1024/1024))
        if MODE==0:
            qbt_client.transfer.speed_limits_mode = True
        else:
            qbt_client.transfer_set_upload_limit(limit=SPEEDLIMIT)

    else:
        print("外网没有设备在播放，Qbit不限速")
        # print("Executing command: {cmd}".format(cmd=COMMAND))
        if MODE==0:
            qbt_client.transfer.speed_limits_mode = False
        else:   
            qbt_client.transfer_set_upload_limit(limit=102400000)

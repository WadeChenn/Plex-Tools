
from mbot.openapi import mbot_api
from mbot.openapi import media_server_manager

#导入插件类
from .plexautoskip import plexautoskip
plexas = plexautoskip()

#获取MR服务
mrserver = mbot_api

#获取plex媒体库
plexserver = media_server_manager.master_plex.plex
servertype='plex'

#设置服务参数
plexas.setdata(plexserver,mrserver,servertype)


from .event import *
# from .command import *

import logging
_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
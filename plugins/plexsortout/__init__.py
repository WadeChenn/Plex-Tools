
from mbot.openapi import mbot_api
from mbot.openapi import media_server_manager

#导入插件类
from .plexsortout import plexsortout
plexst = plexsortout()

#获取MR服务
mrserver = mbot_api

#获取plex媒体库
plexserver = media_server_manager.master_plex.plex
servertype='plex'

#设置服务参数
plexst.setdata(plexserver,mrserver,servertype)


from .event import *
from .command import *

import logging
_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from mbot.openapi import mbot_api
mrserver = mbot_api
from mbot.external.mediaserver import MediaServerInstance
servertype = MediaServerInstance.server_type
plexserver = MediaServerInstance.plex

from .plexchineseactor import plexchineseactor

plexca = plexchineseactor(mrserver,plexserver,servertype)

from .event import *
from .command import *

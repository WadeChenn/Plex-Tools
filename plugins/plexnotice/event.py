import logging
from typing import Dict, Any
import threading
from mbot.core.event.models import EventType
from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext, PluginMeta
import time

from . import plexnt
_LOGGER = logging.getLogger(__name__)

@plugin.after_setup
def main(plugin: PluginMeta, config: Dict):
    UrlType = config.get('UrlType')
    PlexUrl = config.get('PlexUrl')
    _LOGGER.info(
    f"{plugin.manifest.title}加载成功，UrlType:{UrlType},PlexUrl:{PlexUrl}")
    # plexnt.process(config)
    thread = threading.Thread(target=plexnt.process, args=(config,))
    thread.start()

@plugin.config_changed
def config_changed(config: Dict):
    #通知中断
    _LOGGER.info("检测到配置变化,通知中断,休眠5s后重新启动通知")
    plexnt.setflag(True)
    time.sleep(3)
    plexnt.setflag(False)
    thread = threading.Thread(target=plexnt.process, args=(config,))
    thread.start()
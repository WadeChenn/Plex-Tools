import logging
from typing import Dict
import threading

from mbot.core.event.models import EventType
from mbot.core.plugins import PluginContext,PluginMeta,plugin
from . import plexas
_LOGGER = logging.getLogger(__name__)
import time

@plugin.after_setup
def main(plugin: PluginMeta, config: Dict):
    _LOGGER.info(
    f"{plugin.manifest.title}加载成功")
    # plexnt.process(config)
    thread = threading.Thread(target=plexas.start, args=(config,))
    thread.start()

@plugin.config_changed
def config_changed(config: Dict):
    #通知中断
    _LOGGER.info("检测到配置变化,通知中断,休眠5s后重新启动通知")
    plexas.setflag(True)
    time.sleep(3)
    plexas.setflag(False)
    thread = threading.Thread(target=plexas.start, args=(config,))
    thread.start()
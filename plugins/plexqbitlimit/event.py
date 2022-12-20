import logging
from typing import Dict
import threading
from mbot.core.event.models import EventType
from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext, PluginMeta
from . import plexfa
_LOGGER = logging.getLogger(__name__)

@plugin.on_event(
    bind_event=["PlexPlayerEvent"], order=1)
def on_event(ctx: PluginContext, event_type: str, config: Dict):
    #获取qbit配置中所有参数
    QBIT_URL = config.get('QBIT_URL')

    _LOGGER.info(
    f"{plugin.manifest.title}加载成功，QBIT_URL:{QBIT_URL}")
    plexfa.process(config)
    # thread = threading.Thread(target=plexnt.process, args=(config,))
    # thread.start()

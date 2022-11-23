import logging
from typing import Dict
import threading
from mbot.core.event.models import EventType
from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext, PluginMeta
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

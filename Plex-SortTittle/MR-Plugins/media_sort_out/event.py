import logging
from typing import Dict, Any

from mbot.core.event.models import EventType
from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext, PluginMeta
# from .discordmessage import DiscordMessage
from .plexsortout import plexsortout

_LOGGER = logging.getLogger(__name__)
plexst = plexsortout()


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    """
    插件加载并设置完成后触发执行这个函数
    函数接收参数固定。第一个为插件元信息对象，第二个为插件配置（如有）
    """
    # plexst.set_config(config.get('webhook'), config.get('proxy'))
    _LOGGER.info(f'{plugin_meta.manifest.title}加载成功，Webhook: {config.get("webhook")} Proxy: {config.get("proxy")}')


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    """
    如果插件定义了配置信息（manifest.config_field），当用户修改配置文件后，执行这个函数并传递变更后的配置信息
    函数接收参数固定。只有一个变更后的配置内容
    """
    # plexst.set_config(config.get('webhook'), config.get('proxy'))


@plugin.on_event(
    bind_event=[EventType.DownloadCompleted], order=1)
def on_event(ctx: PluginContext, event_type: str, data: Dict):
    """
    触发绑定的事件后调用此函数
    函数接收参数固定。第一个为插件上下文信息，第二个事件类型，第三个事件携带的数据
    """
    plexst.process()
    # plexst.send_by_event(event_type, data)
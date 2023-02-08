import logging
from typing import Dict

from mbot.core.event.models import EventType
from mbot.core.plugins import PluginContext,PluginMeta,plugin
from . import plexst
_LOGGER = logging.getLogger(__name__)

@plugin.after_setup
def after_setup(plugin: PluginMeta, plugin_conf: dict):
    """
    插件加载后执行的操作
    """
    _LOGGER.info('插件加载完成')
    libstr = plugin_conf.get('LIBRARY')
    if libstr:
        libtable=libstr.split(',')
        _LOGGER.info(libtable)

        plugin_conf['library']=libtable
    else:
        _LOGGER.info('未设置LIBRARY')
        plugin_conf['library'] = 'ALL'
    plexst.setconfig(plugin_conf)
    _LOGGER.info('SortOut参数设置完成')
    # printAllMembers(plexst)


def printAllMembers(cls):
    print('\n'.join(dir(cls)))

@plugin.on_event(
    bind_event=['PlexActivityEvent'], order=1)
def on_event(ctx: PluginContext, event_type: str, data: Dict):
    """
    触发绑定的事件后调用此函数
    函数接收参数固定。第一个为插件上下文信息，第二个事件类型，第三个事件携带的数据
    """
    if data.get('Activity') == 'Added' and data.get('Added'):
        plexst.process()
    # plexst.send_by_event(event_type, data)
@plugin.on_event(
    bind_event=[EventType.DownloadCompleted], order=1)
def on_event(ctx: PluginContext, event_type: str, data: Dict):
    """
    触发绑定的事件后调用此函数
    函数接收参数固定。第一个为插件上下文信息，第二个事件类型，第三个事件携带的数据
    """
    if not data.get('Added'):
        plexst.process()
    # plexst.send_by_event(event_type, data)

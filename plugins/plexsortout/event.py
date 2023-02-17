import logging
from typing import Dict

from mbot.core.event.models import EventType
from mbot.core.plugins import PluginContext,PluginMeta,plugin
from . import plexst
_LOGGER = logging.getLogger(__name__)
plugins_name = '「PLEX 工具箱」'

@plugin.after_setup
def after_setup(plugin: PluginMeta, plugin_conf: dict):
    """
    插件加载后执行的操作
    """
    _LOGGER.info(f'{plugins_name}插件加载完成')
    libstr = plugin_conf.get('LIBRARY')
    if libstr:
        libtable=libstr.split(',')
        _LOGGER.info(f'{plugins_name}需要整理的库：{libtable}')

        plugin_conf['library']=libtable
    else:
        _LOGGER.info(f'{plugins_name}未设置需要整理的媒体库名称')
        plugin_conf['library'] = 'ALL'
    plexst.setconfig(plugin_conf)
    _LOGGER.info(f'{plugins_name}参数设置完成')
    # printAllMembers(plexst)

@plugin.config_changed
def config_changed(plugin_conf: dict):
    """
    插件变更配置后执行的操作
    """
    _LOGGER.info(f'{plugins_name}插件加载完成')
    libstr = plugin_conf.get('LIBRARY')
    if libstr:
        libtable=libstr.split(',')
        _LOGGER.info(f'{plugins_name}需要整理的库：{libtable}')

        plugin_conf['library']=libtable
    else:
        _LOGGER.info(f'{plugins_name}未设置需要整理的媒体库名称')
        plugin_conf['library'] = 'ALL'
    plexst.setconfig(plugin_conf)
    _LOGGER.info(f'{plugins_name}参数设置完成')


def printAllMembers(cls):
    print('\n'.join(dir(cls)))

@plugin.on_event(
    bind_event=['PlexActivityEvent'], order=1)
def on_event(ctx: PluginContext, event_type: str, data: Dict):
    """
    触发绑定的事件后调用此函数
    函数接收参数固定。第一个为插件上下文信息，第二个事件类型，第三个事件携带的数据
    """
    _LOGGER.info(f'{plugins_name}接收到「PlexActivityEvent」事件，开始整理')
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
    _LOGGER.info(f'{plugins_name}接收到「DownloadCompleted」事件，开始整理')
    if not data.get('Added'):
        plexst.process()
    # plexst.send_by_event(event_type, data)

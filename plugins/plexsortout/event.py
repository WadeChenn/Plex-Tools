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
    _LOGGER.info(f'{plugins_name}插件开始加载')
    global added, libtable
    added = plugin_conf.get('Added') if plugin_conf.get('Added') else None
    if added:
        _LOGGER.info(f'{plugins_name}使用「PLEX入库事件」作为触发运行')
    else:
        _LOGGER.info(f'{plugins_name}使用「MR 下载完成事件」作为触发运行')
    libstr = plugin_conf.get('LIBRARY')
    if libstr:
        libtable=libstr.split(',')
        _LOGGER.info(f'{plugins_name}需要整理的库：{libtable}')
        plugin_conf['library']=libtable
    else:
        _LOGGER.info(f'{plugins_name}未设置需要整理的媒体库名称')
        plugin_conf['library'] = 'ALL'
    plexst.setconfig(plugin_conf)
    _LOGGER.info(f'{plugins_name}自定义参数加载完成')
    # printAllMembers(plexst)

@plugin.config_changed
def config_changed(plugin_conf: dict):
    """
    插件变更配置后执行的操作
    """
    _LOGGER.info(f'{plugins_name}配置发生变更，加载新配置')
    global added, libtable
    added = plugin_conf.get('Added') if plugin_conf.get('Added') else None
    if added:
        _LOGGER.info(f'{plugins_name}使用「PLEX入库事件」作为触发运行')
    else:
        _LOGGER.info(f'{plugins_name}使用「MR 下载完成事件」作为触发运行')
    libstr = plugin_conf.get('LIBRARY')
    if libstr:
        libtable=libstr.split(',')
        _LOGGER.info(f'{plugins_name}需要整理的库：{libtable}')

        plugin_conf['library']=libtable
    else:
        _LOGGER.info(f'{plugins_name}未设置需要整理的媒体库名称')
        plugin_conf['library'] = 'ALL'
    plexst.setconfig(plugin_conf)
    _LOGGER.info(f'{plugins_name}自定义参数加载完成')

def printAllMembers(cls):
    print('\n'.join(dir(cls)))

@plugin.on_event(
    bind_event=['PlexActivityEvent'], order=1)
def on_event(ctx: PluginContext, event_type: str, data: Dict):
    """
    触发绑定的事件后调用此函数
    函数接收参数固定。第一个为插件上下文信息，第二个事件类型，第三个事件携带的数据
    """
    # _LOGGER.info(f'{plugins_name}接收到「PlexActivityEvent」事件，开始整理')
    if data.get('Activity') == 'Added' and added:
        _LOGGER.info(f'{plugins_name}接收到「PLEX 入库」事件，开始整理')
        plexst.process()
    # plexst.send_by_event(event_type, data)
@plugin.on_event(
    bind_event=[EventType.DownloadCompleted], order=1)
def on_event(ctx: PluginContext, event_type: str, data: Dict):
    """
    触发绑定的事件后调用此函数
    函数接收参数固定。第一个为插件上下文信息，第二个事件类型，第三个事件携带的数据
    """
    # _LOGGER.info(f'{plugins_name}接收到「DownloadCompleted」事件，现在开始整理')
    if not added:
        _LOGGER.info(f'{plugins_name}接收到「下载完成」事件，且未开启入库事件触发，现在开始整理')
        plexst.process()
    else:
        _LOGGER.info(f'{plugins_name}接收到「下载完成」事件，但已开启入库事件触发，将等待 PLEX 入库后再整理')
    # plexst.send_by_event(event_type, data)

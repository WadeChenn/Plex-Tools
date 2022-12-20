from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from . import plexca
from mbot.openapi import mbot_api
from mbot.core.params import ArgSchema, ArgType
import logging
_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
def get_enum_data():
    """
    返回一个包含name和value的枚举数据，在前端页面会呈现为下拉列表框；
    value就是你最终你能接收到的变量值
    """
    _LOGGER.info('开始获取媒体库')
    libtable = plexca.get_library()
    return libtable


@plugin.command(name='select_data', title='Plex中文演员', desc='自动添加中文演员', icon='StarRate')
def select_data(
        ctx: PluginCommandContext,
        library: ArgSchema(ArgType.Enum, '媒体库', '选择一个媒体库', enum_values=get_enum_data, multi_value=True)
):
    plexca.process_all(library)
    user_list = list(filter(lambda x: x.role == 1, mbot_api.user.list()))
    if user_list:
        for user in user_list:
            mbot_api.notify.send_system_message(user.uid, 'Plex添加中文演员',
                                                '自动添加中文演员完毕')
    return PluginCommandResponse(True, f'Plex添加完成')

@plugin.command(name='refresh_data', title='Plex解锁演员', desc='解锁中文演员并刷新元数据(解决老版插件锁定演员问题,运行过老版插件的需先运行一次)', icon='StarRate')
def refresh_data(
        ctx: PluginCommandContext,
        library: ArgSchema(ArgType.Enum, '媒体库', '选择一个媒体库', enum_values=get_enum_data, multi_value=True)
):
    plexca.refreshmeta(library)
    user_list = list(filter(lambda x: x.role == 1, mbot_api.user.list()))
    if user_list:
        for user in user_list:
            mbot_api.notify.send_system_message(user.uid, 'Plex解锁演员',
                                                '自动解锁中文演员并刷新元数据')
    return PluginCommandResponse(True, f'Plex刷新完成')
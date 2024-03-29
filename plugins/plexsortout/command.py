from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse,PluginMeta
from . import plexst
from mbot.openapi import mbot_api
from mbot.core.params import ArgSchema, ArgType

import logging
_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

plugins_name = '「PLEX 工具箱」'

def get_enum_data():
    """
    返回一个包含name和value的枚举数据，在前端页面会呈现为下拉列表框；
    value就是你最终你能接收到的变量值
    """
    _LOGGER.info(f'{plugins_name}开始获取媒体库')
    libtable=plexst.get_library()
    return libtable

@plugin.command(name='select_data', title='Plex整理全库', desc='自动翻译标签&&拼音排序&&添加TOP250标签', icon='HourglassFull',run_in_background=True)
def select_data(ctx: PluginCommandContext,
                library: ArgSchema(ArgType.Enum, '选择需要整理的媒体库', '', enum_values=get_enum_data,multi_value=True),
                sortoutNum: ArgSchema(ArgType.String, '整理数量，示例：50，表示只整理最新的50条，留空整理全部', '', default_value='ALL', required=False)):

    # plexst.config['library']=library
    plexst.process_all(library,sortoutNum)
    user_list = list(filter(lambda x: x.role == 1, mbot_api.user.list()))
    if user_list:
        for user in user_list:
            mbot_api.notify.send_system_message(user.uid, '手动运行 Plex 媒体库整理',
                                                '翻译标签 && 拼音排序 && 添加TOP250标签完毕')
    return PluginCommandResponse(True, f'手动运行 Plex 媒体库整理完成')


# @plugin.command(name='plexcollection', title='Plex整理合集首字母', desc='自动整理合集首字母', icon='HourglassFull',run_in_background=True)
# def echo_c(ctx: PluginCommandContext):
#     plexst.process_collections()
#     user_list = list(filter(lambda x: x.role == 1, mbot_api.user.list()))
#     if user_list:
#         for user in user_list:
#             mbot_api.notify.send_system_message(user.uid, 'Plex整理合集首字母',
#                                                 '自动整理合集首字母')
#     return PluginCommandResponse(True, f'Plex合集整理完成')

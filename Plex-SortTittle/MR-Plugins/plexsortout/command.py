from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from . import plexst
from mbot.openapi import mbot_api


@plugin.command(name='async', title='Plex整理全库', desc='自动翻译标签&&拼音排序&&添加TOP250标签', icon='HourglassFull',
                run_in_background=True)
def echo(ctx: PluginCommandContext):
    plexst.process_all()
    user_list = list(filter(lambda x: x.role == 1, mbot_api.user.list()))
    if user_list:
        for user in user_list:
            mbot_api.notify.send_system_message(user.uid, 'Plex媒体库整理',
                                                '自动翻译标签&&拼音排序&&添加TOP250标签完毕')
    return PluginCommandResponse(True, f'Plex整理完成')

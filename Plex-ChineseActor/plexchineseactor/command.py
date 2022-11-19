from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from . import plexca
from mbot.openapi import mbot_api


@plugin.command(name='async', title='Plex中文演员', desc='自动添加中文演员', icon='HourglassFull',
                run_in_background=True)
def echo(ctx: PluginCommandContext):
    plexca.process_all()
    user_list = list(filter(lambda x: x.role == 1, mbot_api.user.list()))
    if user_list:
        for user in user_list:
            mbot_api.notify.send_system_message(user.uid, 'Plex添加中文演员',
                                                '自动添加中文演员完毕')
    return PluginCommandResponse(True, f'Plex添加完成')
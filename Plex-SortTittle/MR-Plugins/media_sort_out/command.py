import time

from mbot.core.params import ArgSchema, ArgType
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from .plexsortout import plexsortout
plexst = plexsortout()


# @plugin.command(name='echo', title='Hello', desc='hello world!', icon='StarRate')
# def echo(ctx: PluginCommandContext, name: ArgSchema(ArgType.String, '昵称', '你叫什么名字')):
#     return PluginCommandResponse(True, f'你好，{name}！')


@plugin.command(name='async', title='Plex整理全库', desc='点击待整理完毕后通知', icon='HourglassFull', run_in_background=True)
def echo(ctx: PluginCommandContext):
    # time.sleep(5)
    plexst.process_all()
    return PluginCommandResponse(True, f'Plex整理完成')

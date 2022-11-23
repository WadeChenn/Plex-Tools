SERVER_URL="http://mr.0bm.cn:60"
ACCESS_KEY="seVcjIU36mW7AXKEQ5DHFfNpw4lyJqxO"
from moviebotapi import MovieBotServer
from moviebotapi.core.models import MediaType
from moviebotapi.core.session import AccessKeySession
mrserver = MovieBotServer(AccessKeySession(SERVER_URL, ACCESS_KEY))
from config import *
from plexnotice import *
if __name__ == '__main__':
    #get param
    config=  {
        'UrlType':0,
        'PlexUrl':'http://plex.0bm.cn:32400',
    }
    if ENABLE_LOG:
        print("--------------------------------------")
        print("正在连接PLEX服务器...")
        print("PLEX_URL = "+PLEX_URL)
        print("PLEX_TOKEN = "+PLEX_TOKEN)
    try:

        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        ws=WebSocketListener(plex)
        updater = WatchStateUpdater(plex,config,mrserver)
        ws.on(
            PlaySessionStateNotification,
            updater.on_play,
            state=["playing", "stopped", "paused"],
        )
        ws.on(
            TimelineEntry,
            updater.on_activity,
            metadataState="created",
            state=5,
        )
        ws.listen()
        _LOGGER.info(f'PlexNoticeStartListen!')
        while True:
            time.sleep(1)
    except Exception as e:
        print(e)
        # 发生异常所在的文件
        print(e.__traceback__.tb_frame.f_globals["__file__"])
        # 发生异常所在的行数
        print(e.__traceback__.tb_lineno)
        print("plex url 或 token错误!")
        os._exit()
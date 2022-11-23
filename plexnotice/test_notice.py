SERVER_URL="http://mr.0bm.cn:60"
ACCESS_KEY="seVcjIU36mW7AXKEQ5DHFfNpw4lyJqxO"
PLEX_TOKEN="xNjbvCpt-P1898dyDACz"            #Plextoken获取,具体方法请自行查找 "zZzxxxxxxxJssiw2zcy" *必须设置
PLEX_URL="http://plex.beimou.net:32400"         #Plexurl "http://plex.xxx.cn:32400" *必须设置
from moviebotapi import MovieBotServer
from moviebotapi.core.models import MediaType
from moviebotapi.core.session import AccessKeySession
mrserver = MovieBotServer(AccessKeySession(SERVER_URL, ACCESS_KEY))
# from config import *
from plexnotice import *

if __name__ == '__main__':
    #get param
    config=  {
        'UrlType':0,
        'PlexUrl':'http://plex.0bm.cn:32400',
        'PlayTitle':'{icon}{title} @{user} ⭐{rating}"',
        'Play':'{library_name} · {video_resolution} · {bitrate}Mbps · {video_dynamic_range} · {duration}分钟 \n{transcode_decision} ⤷ {quality_profile} · {stream_video_dynamic_range} \n{progress} {progress_percent}% \n播放时间：{datestamp}  周{current_weekday}  {timestamp} \n观看进度：{progress_time}({progress_percent}%)  剩余{remaining_duration}分钟 \n文件大小：{file_size} \n首映日期：{air_date} \n播放设备：{player} · {product} \n设备地址：{ip_address} {country} · {city}',
        'StopTitle':'{icon}{title} @{user} ⭐{rating}"',
        'Stop':'{library_name} · {video_resolution} · {bitrate}Mbps · {video_dynamic_range} · {duration}分钟 \n{transcode_decision} ⤷ {quality_profile} · {stream_video_dynamic_range} \n{progress} {progress_percent}% \n播放时间：{datestamp}  周{current_weekday}  {timestamp} \n观看进度：{progress_time}({progress_percent}%)  剩余{remaining_duration}分钟 \n文件大小：{file_size} \n首映日期：{air_date} \n播放设备：{player} · {product} \n设备地址：{ip_address} {country} · {city}',
    }
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
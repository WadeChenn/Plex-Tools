import re
import logging
import requests
_LOGGER = logging.getLogger(__name__)
##############################################################
import os
from importlib import import_module
from pickle import FALSE, TRUE
import sys
import urllib
import time
import asyncio
from datetime import datetime
from moviebotapi import MovieBotServer
from moviebotapi.core.models import MediaType
from moviebotapi.core.session import AccessKeySession

from .plexevent import (
    ActivityNotification,
    Error,
    PlaySessionStateNotification,
    TimelineEntry,
    EventFactory,
)

########################依赖库初始化###########################
# 依赖库列表
import_list=[
    'plexapi',
]
# 判断依赖库是否安装,未安装则安装对应依赖库
sourcestr = "https://pypi.tuna.tsinghua.edu.cn/simple/"  # 镜像源
def GetPackage(PackageName):
    comand = "pip install " + PackageName +" -i "+sourcestr
    # 正在安装
    print("------------------正在安装" + str(PackageName) + " ----------------------")
    print(comand + "\n")
    os.system(comand)
for v in import_list:
    try:
        import_module(v)
    except ImportError:
        print("Not find "+v+" now install")
        GetPackage(v)
#############################################################
import pypinyin
from plexapi.server import PlexServer
import re
import argparse
from time import sleep
from plexapi.server import PlexServer
# wxtitle='{icon}{title} @{user} ⭐{rating}'
# starttemplate='{art} {themoviedb_url} ▶️{title}" @"{user}"  "{rating} {bitrate} 0:0:0 {progress_percent} {ip_address} '
# wxbody='{library_name} · {video_resolution} · {bitrate}Mbps · {video_dynamic_range} · {duration}分钟 \n{transcode_decision} ⤷ {quality_profile} · {stream_video_dynamic_range} \n{progress} {progress_percent}% \n播放时间：{datestamp}  周{current_weekday}  {timestamp} \n观看进度：{progress_time}({progress_percent}%)  剩余{remaining_duration}分钟 \n文件大小：{file_size} \n首映日期：{air_date} \n播放设备：{player} · {product} \n设备地址：{ip_address} {country} · {city}'

# starttemplate.format(art)
# words = re.findall(r'".*?"',starttemplate)


class WebsocketPlayer:  # pylint: disable=too-few-public-methods
    """Represent an individual player state in the Plex websocket stream."""

    def __init__(self, session_id, state, media_key, position,plex):
        """Initialize a WebsocketPlayer instance."""
        self.session_id = session_id
        self.state = state
        self.media_key = media_key
        self.position = position
        self.timestamp = datetime.now()
        self.username = 'username'
        self.address = 'address'
        self.title = 'title'
        self.playerproduct = 'playerproduct'
        self.product = 'product'
        self.transcode={}
        self.transcode['istrans']=0
        self.transcode['quality_profile']=''
        sessions = plex.sessions()
        bandwidth=0
        for session in sessions:
            if session.TYPE=='track':
                continue
            sk=session.sessionKey
            if str(sk)==self.session_id:
                username=session.usernames[0]
                for player in session.players:
                    # print(session.title+state+player.state)
                    address=player.address
                    self.username = username
                    self.address = address
                    self.title = session.title
                    self.product = player.product
                    self.playerproduct = player.title

                if session.transcodeSession:
                    self.transcode['istrans']=1
                    self.transcode['quality_profile']=str(session.media[0].width)+'p · '+str(round(session.media[0].bitrate/1024,1))
                else:
                    self.transcode['istrans']=0
    def significant_position_change(self, timestamp, new_position):
        """Determine if position change indicates a seek."""
        timediff = (timestamp - self.timestamp).total_seconds()
        posdiff = (new_position - self.position) / 1000
        diffdiff = timediff - posdiff
        if abs(diffdiff) > 5:
            return True
        return False

class EventDispatcher:
    def __init__(self):
        self.event_listeners = list()
        self.event_factory = EventFactory()

    def on(self, event_type, listener, **kwargs):
        self.event_listeners.append(
            {
                "listener": listener,
                "event_type": event_type,
                "filters": kwargs,
            }
        )
        return self

    def event_handler(self, data):
        # self.logger.debug(data)
        # print(data)
        if isinstance(data, Error):
            return self.dispatch(data)

        events = self.event_factory.get_events(data)
        for event in events:
            self.dispatch(event)

    def dispatch(self, event):
        for listener in self.event_listeners:
            if not self.match_event(listener, event):
                continue

            listener["listener"](event)

    @staticmethod
    def match_filter(event, key, match):
        if not hasattr(event, key):
            return False
        value = getattr(event, key)

        # check for arrays
        if isinstance(match, list):
            return value in match

        # check for scalars
        return value == match

    def match_event(self, listener, event):
        if not isinstance(event, listener["event_type"]):
            return False

        if listener["filters"]:
            for name, value in listener["filters"].items():
                if not self.match_filter(event, name, value):
                    return False

        return True


class WebSocketListener:
    def __init__(self, plex: PlexServer, poll_interval=5, restart_interval=15):
        self.plex = plex
        self.poll_interval = poll_interval
        self.restart_interval = restart_interval
        self.dispatcher = EventDispatcher()
        # self.db_stream

        self.players = {}
    def on(self, event_type, listener, **kwargs):
        self.dispatcher.on(event_type, listener, **kwargs)

    def listen(self):
        while True:
            notifier = self.plex.startAlertListener(
                callback=self.dispatcher.event_handler
            )
            while notifier.is_alive():
                sleep(self.poll_interval)

            self.dispatcher.event_handler(Error(msg="Server closed connection"))
            sleep(self.restart_interval)
class WatchStateUpdater:
    def __init__(
        self,
        plex,
        config,
        mrserver
    ):
        # pass
        self.players = {}
        self.plex = plex
        self.config = config
        self.mrserver = mrserver

    def player_event(self, msg):
        """Determine if messages relate to an interesting player event."""
        should_fire = False

        payload = msg
        try:
            session_id = payload["sessionKey"]
            state = payload["state"]
            media_key = payload["key"]
            position = payload["viewOffset"]
            if session_id not in self.players:
                self.players[session_id] = WebsocketPlayer(
                    session_id, state, media_key, position,self.plex
                )
                print("New session: %s", payload)
                temp={
                    'title':self.config.get('PlayTitle'),
                    'body':self.config.get('Play')
                }
                self.processmsg(payload,'start',self.players[session_id],temp)
                return True

            if state == "stopped":
                # Sessions "end" when stopped
                temp={
                    'title':self.config.get('PlayTitle'),
                    'body':self.config.get('Play')
                }
                self.processmsg(payload,'stop',self.players[session_id],temp)
                self.players.pop(session_id)
                print("Session ended: %s", payload)
                return True

            player = self.players[session_id]
            now = datetime.now()

            # Ignore buffering states as transient
            if state != "buffering":
                if player.media_key != media_key or player.state != state:
                    # State or playback item changed
                    print("State/media changed: %s", payload)
                    sessions = self.plex.sessions()
                    for session in sessions:
                        sk=session.sessionKey
                        if str(sk)==session_id:
                            if session.transcodeSession:
                                player.transcode['istrans']=1
                                player.transcode['quality_profile']=str(session.media[0].width)+'p · '+str(round(session.media[0].bitrate/1024,1))+'Mbp'
                            else:
                                player.transcode['istrans']=0
                    # self.processmsg(payload,'start',self.players[session_id])

                    # if state=='paused':
                    #     self.processmsg(payload,'paused')
                    should_fire = True
                elif state == "playing" and player.significant_position_change(
                    now, position
                ):
                    # Client continues to play and a seek was detected
                    print("Seek detected: %s", payload)
                    should_fire = True

            player.state = state
            player.media_key = media_key
            player.position = position
            player.timestamp = now
        except Exception as e:
            print(e)
            # 发生异常所在的文件
            print(e.__traceback__.tb_frame.f_globals["__file__"])
            # 发生异常所在的行数
            print(e.__traceback__.tb_lineno)
            print("plex url 或 token错误!")
        return should_fire

    def on_error(self, error: Error):
        # self.logger.error(error.msg)
        self.scrobblers.clear()
        self.sessions.clear()

    def on_activity(self, activity: ActivityNotification):
        activity_temp=activityl
        _LOGGER.info(f'on_activity!')
        pass

    def on_delete(self, event: TimelineEntry):
        print('on_delete')
        pass
    def processmsg(self,event,status,playerse,temp):
        _LOGGER.info('processmsg')
        print('processmsg')
        wxtitle=temp.get('title')
        wxbody=temp.get('body')
        playicon={
            'start':'▶️',
            'stop':'⏹️',
            'resume':'▶️',
            'paused':'⏹️',
            'add':'🍿',
        }
        week={
            0:"一",
            1:"二",
            2:"三",
            3:"四",
            4:"五",
            5:"六",
            6:"日",
        }
        trans={
            0:"原始播放",
            1:"转码播放"
        }

        key=event['key'] #媒体key
        sessionkey=event['sessionKey']
        state=event['state'] #播放状态
        viewOffset=event['viewOffset'] #播放进度
        section=self.plex.library.fetchItems(key)[0]
        #获取媒体
        section_media=section.media[0]
        #获取视频流
        streams=section_media.parts[0].streams[0]

        file_size=round(section_media.parts[0].size/1024/1024/1024,1)
        #检测是否剧集,是 查找爷节点
        if section.TYPE=="episode":
            show=self.plex.library.fetchItems(section.grandparentKey)[0]
            tmdb_id=show.guids[1].id.split('//')[1]
            media_type=MediaType.TV
            rating=show.audienceRating
            air_date='{year}-{month}-{day}'.format(year=show.originallyAvailableAt.year,month=show.originallyAvailableAt.month,day=show.originallyAvailableAt.day)
            title=section.grandparentTitle
            art=show.art
        else:
            bitrate=section_media.parts[0].streams[0].bitrate
            air_date='{year}-{month}-{day}'.format(year=section.originallyAvailableAt.year,month=section.originallyAvailableAt.month,day=section.originallyAvailableAt.day)
            rating=section.audienceRating
            title=playerse.title
            tmdb_id=section.guids[1].id.split('//')[1]
            media_type=MediaType.Movie
            art=section.art
        bitrate=section_media.parts[0].streams[0].bitrate
        container=section_media.container
        Codec=section_media.videoCodec
        resolution=section_media.videoResolution
        library=section.librarySectionTitle
        current_weekday='current_weekday'
        remaining_duration='remaining_duration'
        timestamp='{hour}:{minute}:{second}'.format(hour=playerse.timestamp.hour,minute=playerse.timestamp.minute,second=playerse.timestamp.second)
        datestamp='{year}-{month}-{day}'.format(year=playerse.timestamp.year,month=playerse.timestamp.month,day=playerse.timestamp.day)
        color_space = streams.colorSpace
        DOVI_profile = streams.DOVIProfile
        bit_depth = streams.bitDepth
        stream_video_dynamic_range='SDR'
        #动态范围判断
        if color_space==None:
            HDR=False
        else:
            HDR = bool(bit_depth > 8 and 'bt2020' in color_space)
        DV = bool(DOVI_profile)
        if not HDR and not DV:
            video_dynamic_range = 'SDR'
        elif HDR:
            video_dynamic_range = 'HDR'
        elif DV:
            video_dynamic_range = 'DV'

        if playerse.transcode['quality_profile']:
            quality_profile=playerse.transcode['quality_profile']
        else:
            quality_profile=''

        #转码判断
        transcode_decision=trans[playerse.transcode['istrans']]
        if playerse.transcode['istrans']==0:
            quality_profile='直接播放'
            stream_video_dynamic_range=''

        current_weekday=week[playerse.timestamp.weekday()]
        address=playerse.address
        username=playerse.username
        artUrl =section.artUrl
        token=section.artUrl.split('Plex-Token=')[1]
        if self.config.get('UrlType'=='1'):
            tmdbinfo=self.mrserver.tmdb.get(media_type, tmdb_id)
            artUrl='https://image.tmdb.org/t/p/w500'+tmdbinfo.backdrop_path
        elif self.config.get('PlexUrl')!='ispublic':
            artUrl=self.config.get('PlexUrl')+art+'?X-Plex-Token='+token

        duration=str(section_media.parts[0].duration//60000)   #单位分钟

        # rating=section.audienceRating
        Codec=section_media.videoCodec
        library=section.librarySectionTitle
        video_resolution=section_media.videoResolution
        player=playerse.playerproduct
        product=playerse.product

        viewOffset=viewOffset//1000
        second=viewOffset%60
        minute=(viewOffset-viewOffset//3600*3600)//60
        hour=viewOffset//3600
        # progress_time=str(hour)+':'+str(minute)+':'+str(second)
        progress_time='{hour}:{minute}:{second}'.format(hour=hour,minute=minute,second=second)

                # air_date='{year}-{month}-{day}'.format(year=show.originallyAvailableAt.year,month=show.originallyAvailableAt.month,day=show.originallyAvailableAt.day)
        remaining_duration=round(float(duration)-viewOffset/60,1)
        progress_percent=int(round(viewOffset/60/float(duration)*100,0))
        bitrate = ('%.1f' %(float(bitrate)/1000))
        #ip归属地查询
        # r=requests.post(url='http://ip-api.com/json/{ip}?lang=zh-CN'.format(ip=address))
        # locate=r.json()
        # country=locate.get('country')
        # city=locate.get('city')
        city=''
        country=''

        # 进度条
        progress = progress_percent
        progress_all_num = 21
        progress_do_text = "■"
        progress_undo_text = "□"
        progress_do_num = round(0.5 + ((progress_all_num * int(progress)) / 100))
        # 处理96%-100%进度时进度条展示，正常计算时，进度大于等于96%就已是满条，需单独处理
        if 95 < int(progress) < 100:
            progress_do_num = progress_all_num - 1

        progress_undo_num = progress_all_num - progress_do_num
        progress_do = progress_do_text * progress_do_num
        progress_undo = progress_undo_text * progress_undo_num
        progress = progress_do + progress_undo

        qry={
            'icon':playicon[status],
            'bitrate':bitrate, #码率 单位Mbps
            'ip_address':address, #IP地址
            'art':artUrl, #图片链接
            'title':title, #标题
            'user':username, #用户名
            'library_name':library, #库名
            'themoviedb_url':artUrl, #TMDB链接
            'progress_percent':progress_percent, #播放百分比
            'transcode_decision':transcode_decision, #是否转码
            'quality_profile':quality_profile, #转码质量
            'timestamp':timestamp, #当天时间
            'progress_time':progress_time, #
            'video_resolution':video_resolution, #媒体分辨率
            'video_dynamic_range':video_dynamic_range, #动态范围
            'rating':rating, #分数
            'stream_video_dynamic_range':stream_video_dynamic_range, #转码后动态范围
            'duration':duration, #总时长
            'datestamp':datestamp, #播放日期
            'product':product, #设备
            'player':player, #播放器
            'air_date':air_date, #出品日期
            'file_size':file_size, #文件大小
            'current_weekday':current_weekday, #星期几
            'remaining_duration':remaining_duration, #剩余时长
            'country':country, #ip归属地(国)
            'city':city, #ip归属地(市)
            'progress':progress,#进度条

        }



        #模板赋值
        wxtitledst=wxtitle.format(**qry)
        wxbodydst= wxbody.format(**qry)
        # print(artUrl)
        print(wxtitledst)
        print(wxbodydst)

        _LOGGER.info(wxtitledst)
        _LOGGER.info(wxbodydst)
        #微信推送
        self.mrserver.notify.send_message_by_tmpl('{{title}}', '{{a}}', {
                'title': wxtitledst,
                'a': wxbodydst,
                'link_url': artUrl,
                'pic_url': artUrl
            },1)
        
    def on_play(self, event: PlaySessionStateNotification):
        print('on_play')
        _LOGGER.info(f'on_play')
        # should_fire = False
        try:
            self.player_event(event)
        except Exception as e:
            print(e)
            # 发生异常所在的文件
            print(e.__traceback__.tb_frame.f_globals["__file__"])
            # 发生异常所在的行数
            print(e.__traceback__.tb_lineno)
            print("plex url 或 token错误!")

    def can_scrobble(self, event: PlaySessionStateNotification):
        if not self.username_filter:
            return True

        return self.sessions[event.session_key] == self.username_filter
 
class plexnotice:
    def process(self,config):
        from mbot.external.mediaserver import MediaServerInstance
        from mbot.openapi import mbot_api
        mrserver = mbot_api
        #get param
        try:
            _LOGGER.info(f'PlexNoticeStartListen!'+PLEX_URL+PLEX_TOKEN)
            servertype = MediaServerInstance.server_type
            servertype="plex"
            if servertype == "plex":
                plex = MediaServerInstance.plex
                ws=WebSocketListener(plex)
                # config=''
                updater = WatchStateUpdater(plex,config,mrserver)
                ws.on(
                    PlaySessionStateNotification,
                    updater.on_play,
                    state=["playing", "stopped", "paused"],
                )
                ws.on(
                    ActivityNotification,
                    updater.on_activity,
                    type="library.refresh.items",
                    event="ended",
                    progress=100,
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
            print("plex url 或 token错误!")
            os._exit()
        if ENABLE_LOG:
            print("服务器连接成功")
            print("--------------------------------------")
            print("Start Serching!")
            print("--------------------------------------")


    
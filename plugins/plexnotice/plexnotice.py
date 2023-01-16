import logging
import requests

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
import pytz
##############################################################
import os
from importlib import import_module
import time
# from datetime import datetime
from moviebotapi.core.models import MediaType
# import apscheduler as ac
from apscheduler.triggers.date import DateTrigger
import datetime
from plugins.plexnotice.lib.activity_handler import TimelineHandler
# import plexpy
from plugins.plexnotice.lib.plexevent import (
    ActivityNotification,
    Error,
    PlaySessionStateNotification,
    TimelineEntry,
    EventFactory,
)
RECENTLY_ADDED_QUEUE = {}
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
ACTIVITY_SCHED = BackgroundScheduler(timezone=pytz.UTC)
########################依赖库初始化###########################
# 依赖库列表
import_list = [
    'plexapi',
]
# 判断依赖库是否安装,未安装则安装对应依赖库
sourcestr = "https://pypi.tuna.tsinghua.edu.cn/simple/"  # 镜像源



def GetPackage(PackageName):
    comand = "pip install " + PackageName + " -i " + sourcestr
    # 正在安装
    print("------------------正在安装" + str(PackageName) + " ----------------------")
    print(comand + "\n")
    os.system(comand)


for v in import_list:
    try:
        import_module(v)
    except ImportError:
        print("Not find " + v + " now install")
        GetPackage(v)
#############################################################
from time import sleep
from plexapi.server import PlexServer


# wxtitle='{icon}{title} @{user} ⭐{rating}'
# starttemplate='{art} {themoviedb_url} ▶️{title}" @"{user}"  "{rating} {bitrate} 0:0:0 {progress_percent} {ip_address} '
# wxbody='{library_name} · {video_resolution} · {bitrate}Mbps · {video_dynamic_range} · {duration}分钟 \n{transcode_decision} ⤷ {quality_profile} · {stream_video_dynamic_range} \n{progress} {progress_percent}% \n播放时间：{datestamp}  周{current_weekday}  {timestamp} \n观看进度：{progress_time}({progress_percent}%)  剩余{remaining_duration}分钟 \n文件大小：{file_size} \n首映日期：{air_date} \n播放设备：{player} · {product} \n设备地址：{ip_address} {country} · {city}'

# starttemplate.format(art)
# words = re.findall(r'".*?"',starttemplate)


class WebsocketPlayer:  # pylint: disable=too-few-public-methods
    """Represent an individual player state in the Plex websocket stream."""

    def __init__(self, session_id, state, media_key, position, plex):
        """Initialize a WebsocketPlayer instance."""
        self.session_id = session_id
        self.state = state
        self.media_key = media_key
        self.position = position
        self.timestamp = datetime.datetime.now()
        self.username = 'username'
        self.address = 'address'
        self.title = 'title'
        self.playerproduct = 'playerproduct'
        self.product = 'product'
        self.transcode = {}
        self.transcode['istrans'] = 0
        self.transcode['quality_profile'] = ''
        sessions = plex.sessions()
        bandwidth = 0
        for session in sessions:
            if session.TYPE == 'track':
                continue
            sk = session.sessionKey
            if str(sk) == self.session_id:
                username = session.usernames[0]
                for player in session.players:
                    # print(session.title+state+player.state)
                    address = player.address
                    self.username = username
                    self.address = address
                    self.title = session.title
                    self.product = player.product
                    self.playerproduct = player.title

                if len(session.transcodeSessions) > 0:
                    self.transcode['istrans'] = 1
                    self.transcode['quality_profile'] = str(session.media[0].width) + 'p · ' + str(
                        round(session.media[0].bitrate / 1024, 1)) + 'Mbps'
                else:
                    self.transcode['istrans'] = 0

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
        _LOGGER.debug(data)
        # print(data)
        # data=
        # data={'type': 'timeline', 'size': 1, 'TimelineEntry': [{'identifier': 'com.plexapp.plugins.library', 'sectionID': '8', 'itemID': '40010', 'type': 4, 'title': '斗罗大陆 S01 E235', 'state': 5, 'updatedAt': 1669339641}]}
        # data={'type': 'timeline', 'size': 1, 'TimelineEntry': [{'identifier': 'com.plexapp.plugins.library', 'sectionID': '8',
        #                                   'itemID': '40011', 'parentItemID': '10653', 'rootItemID': '10652', 'type': 4,
        #                                   'title': '', 'state': 0, 'metadataState': 'created', 'updatedAt': 1669341621}]}
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


# RECENTLY_ADDED_QUEUE = {}
# ACTIVITY_SCHED = None


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
        self.MBlacklist = self.config.get('MemberBlackList')
        self.LBlacklist = self.config.get('LibBlackList')

    def player_event(self, msg):
        """Determine if messages relate to an interesting player event."""
        should_fire = False

        payload = msg
        # try:
        session_id = payload["sessionKey"]
        state = payload["state"]
        media_key = payload["key"]
        position = payload["viewOffset"]

        if session_id not in self.players:
            self.players[session_id] = WebsocketPlayer(
                session_id, state, media_key, position, self.plex
            )
            _LOGGER.info("New session: %s", payload)
            temp = {
                'title': self.config.get('PlayTitle'),
                'body': self.config.get('Play')
            }
            self.mrserver.event.publish_event('PlexPlayerEvent', {
                'player': 'play'
            })
            self.processmsg(payload, 'start', self.players[session_id], temp)
            return True

        if state == "stopped":
            self.mrserver.event.publish_event('PlexPlayerEvent', {
                'player': 'stopped'
            })
            # if playerse.title=='title' and playerse.username=='username':
            #     return
            # Sessions "end" when stopped
            temp = {
                'title': self.config.get('PlayTitle'),
                'body': self.config.get('Play')
            }
            player = self.players[session_id]
            stopnow = datetime.datetime.now()
            timediff = (stopnow - player.timestamp).total_seconds()
            if timediff > 5:
                self.processmsg(payload, 'stop', self.players[session_id], temp)
            else:
                _LOGGER.info('播放时间过短,不进行通知')

            self.players.pop(session_id)
            _LOGGER.info("Session ended: %s", payload)
            return True

        player = self.players[session_id]
        now = datetime.datetime.now()

        # Ignore buffering states as transient
        if state != "buffering":
            if player.media_key != media_key or player.state != state:
                # State or playback item changed
                self.mrserver.event.publish_event('PlexPlayerEvent', {
                    'player': 'changed'
                })
                _LOGGER.info("State/media changed: %s", payload)
                sessions = self.plex.sessions()
                for session in sessions:
                    sk = session.sessionKey
                    if str(sk) == session_id:
                        if session.transcodeSession:
                            player.transcode['istrans'] = 1
                            player.transcode['quality_profile'] = str(session.media[0].width) + 'p · ' + str(
                                round(session.media[0].bitrate / 1024, 1)) + 'Mbp'
                        else:
                            player.transcode['istrans'] = 0
                # self.processmsg(payload,'start',self.players[session_id])

                if state=='paused':
                    self.mrserver.event.publish_event('PlexPlayerEvent', {
                        'player': 'paused'
                    })
                    self.processmsg(payload,'paused')
                should_fire = True
            elif state == "playing" and player.significant_position_change(
                    now, position
            ):
                # Client continues to play and a seek was detected
                self.mrserver.event.publish_event('PlexPlayerEvent', {
                    'player': 'seek'
                })
                _LOGGER.info("Seek detected: %s", payload)
                should_fire = True

        player.state = state
        player.media_key = media_key
        player.position = position
        player.timestamp = now
        # except Exception as e:
        # _LOGGER.error(
        #     "{0} {1} 第{2}行".format(e, e.__traceback__.tb_frame.f_globals["__file__"], e.__traceback__.tb_lineno))
        return should_fire

    def on_error(self, error: Error):
        # self._LOGGER.error(error.msg)
        self.scrobblers.clear()
        self.sessions.clear()

    def on_activity(self, activity: ActivityNotification):
        global RECENTLY_ADDED_QUEUE
        global ACTIVITY_SCHED
        timelineHandler = TimelineHandler(activity, self.plex,self.mrserver ,self.config,RECENTLY_ADDED_QUEUE,ACTIVITY_SCHED)
        timelineHandler.process()

        pass

    def on_delete(self, event: TimelineEntry):
        _LOGGER.info('on_delete')
        pass

    def processmsg(self, event, status, playerse, temp):
        try:
            _LOGGER.info('processmsg')
            mbl = self.MBlacklist.split(',')
            lbl = self.LBlacklist.split(',')
            if playerse.username in mbl:
                _LOGGER.info(playerse.username + ' 处于黑名单列表中')
                return
            if playerse.title == 'title' and playerse.username == 'username':
                return


            wxtitle = temp.get('title')
            wxbody = temp.get('body')
            playicon = {
                'start': '▶️',
                'stop': '⏹️',
                'resume': '▶️',
                'paused': '⏹️',
                'add': '🍿',
            }
            week = {
                0: "一",
                1: "二",
                2: "三",
                3: "四",
                4: "五",
                5: "六",
                6: "日",
            }
            trans = {
                0: "直接播放",
                1: "转码播放"
            }

            key = event['key']  # 媒体key
            sessionkey = event['sessionKey']
            state = event['state']  # 播放状态
            viewOffset = event['viewOffset']  # 播放进度
            section = self.plex.library.fetchItems(key)[0]

            library = section.librarySectionTitle
            if library in lbl:
                _LOGGER.info('{0}库处于黑名单不进行通知'.format(library))
                return

            # 获取媒体
            section_media = section.media[0]
            # 获取视频流
            streams = section_media.parts[0].streams[0]

            file_size = round(section_media.parts[0].size / 1024 / 1024 / 1024, 2)
            if file_size < 1:
                file_size = round(file_size * 1000, 0)
                file_size = str(file_size) + 'MB'
            else:
                file_size = str(file_size) + 'GB'

            # 检测是否剧集,是 查找爷节点
            tmdb_id = ''
            if section.TYPE == "episode":
                show = self.plex.library.fetchItems(section.grandparentKey)[0]
                for id in show.guids:
                    if id.id.split('://')[0] == 'tmdb':
                        tmdb_id = id.id.split('//')[1]

                media_type = MediaType.TV
                rating = show.audienceRating
                air_date = '{0}-{1:0>2d}-{2:0>2d}'.format(show.originallyAvailableAt.year,
                                                          show.originallyAvailableAt.month,
                                                          show.originallyAvailableAt.day)
                # air_date = str('{0}{1:0>2d}{2:0>2d}'.format(air_date))
                seasonEpisode = section.seasonEpisode
                seasonEpisode = seasonEpisode.replace('s', 'S')
                seasonEpisode = seasonEpisode.replace('e', '·E')
                title = section.grandparentTitle + seasonEpisode
                # title.replace()
                art = show.art
            else:
                bitrate = section_media.parts[0].streams[0].bitrate
                air_date = '{0}-{1:0>2d}-{2:0>2d}'.format(section.originallyAvailableAt.year,
                                                          section.originallyAvailableAt.month,
                                                          section.originallyAvailableAt.day)
                rating = section.audienceRating
                title = playerse.title
                for id in section.guids:
                    if id.id.split('://')[0] == 'tmdb':
                        tmdb_id = id.id.split('//')[1]
                media_type = MediaType.Movie
                art = section.art
            if rating == None:
                rating = ''

            bitrate = section_media.parts[0].streams[0].bitrate
            container = section_media.container
            Codec = section_media.videoCodec
            resolution = section_media.videoResolution
            library = section.librarySectionTitle
            current_weekday = 'current_weekday'
            remaining_duration = 'remaining_duration'
            timestamp = '{0:0>2d}:{1:0>2d}:{2:0>2d}'.format(playerse.timestamp.hour, playerse.timestamp.minute,
                                                            playerse.timestamp.second)
            datestamp = '{0}-{1:0>2d}-{2:0>2d}'.format(playerse.timestamp.year, playerse.timestamp.month,
                                                       playerse.timestamp.day)

            color_space = streams.colorSpace
            DOVI_profile = streams.DOVIProfile
            bit_depth = streams.bitDepth
            stream_video_dynamic_range = 'SDR'
            # 动态范围判断
            if color_space == None:
                HDR = False
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
                quality_profile = playerse.transcode['quality_profile']
            else:
                quality_profile = ''

            # 转码判断
            transcode_decision = trans[playerse.transcode['istrans']]
            if playerse.transcode['istrans'] == 0:
                quality_profile = '原始质量'
                stream_video_dynamic_range = ''

            current_weekday = week[playerse.timestamp.weekday()]
            address = playerse.address
            username = playerse.username

            artUrl = section.artUrl
            _LOGGER.info('UseTMDB')
            if self.config.get('UseTMDB') and tmdb_id != '':
                tmdbinfo = self.mrserver.tmdb.get(media_type, tmdb_id)
                if tmdbinfo.backdrop_path:
                    artUrl = 'https://image.tmdb.org/t/p/w500' + tmdbinfo.backdrop_path
                else:
                    artUrl='https://s2.loli.net/2022/11/28/P68gBzJ7fnRVO3Z.png'
            elif self.config.get('PlexUrl') != 'ispublic':
                if artUrl != None:
                    token = section.artUrl.split('Plex-Token=')[1]
                    artUrl = self.config.get('PlexUrl') + art + '?X-Plex-Token=' + token
                else:
                    artUrl='https://s2.loli.net/2022/11/28/P68gBzJ7fnRVO3Z.png'

            duration = str(section_media.parts[0].duration // 60000)  # 单位分钟

            # rating=section.audienceRating
            Codec = section_media.videoCodec
            library = section.librarySectionTitle
            video_resolution = section_media.videoResolution
            player = playerse.playerproduct
            product = playerse.product

            viewOffset = viewOffset // 1000
            second = viewOffset % 60
            minute = (viewOffset - viewOffset // 3600 * 3600) // 60
            hour = viewOffset // 3600
            # progress_time=str(hour)+':'+str(minute)+':'+str(second)
            # '{0:0>2d}:{1:0>2d}:{2:0>2d}'.format(playerse.timestamp.hour,playerse.timestamp.minute,playerse.timestamp.second)
            progress_time = '{0:0>2d}:{1:0>2d}:{2:0>2d}'.format(hour, minute, second)

            # air_date='{year}-{month}-{day}'.format(year=show.originallyAvailableAt.year,month=show.originallyAvailableAt.month,day=show.originallyAvailableAt.day)
            remaining_duration = round(float(duration) - viewOffset / 60, 0)
            progress_percent = int(round(viewOffset / 60 / float(duration) * 100, 0))
            bitrate = ('%.1f' % (float(bitrate) / 1000))

            city = ''
            country = ''
            if self.config.get('Locate'):
                _LOGGER.info('归属地查询')
                # ip归属地查询
                r = requests.post(url='http://ip-api.com/json/{ip}?lang=zh-CN'.format(ip=address))
                locate = r.json()
                if locate.get('status') != 'fail':
                    country = locate.get('country')
                    city = locate.get('city')

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

            qry = {
                'icon': playicon[status],
                'bitrate': bitrate,  # 码率 单位Mbps
                'ip_address': address,  # IP地址
                'art': artUrl,  # 图片链接
                'title': title,  # 标题
                'user': username,  # 用户名
                'library_name': library,  # 库名
                'themoviedb_url': artUrl,  # TMDB链接
                'progress_percent': progress_percent,  # 播放百分比
                'transcode_decision': transcode_decision,  # 是否转码
                'quality_profile': quality_profile,  # 转码质量
                'timestamp': timestamp,  # 当天时间
                'progress_time': progress_time,  #
                'video_resolution': video_resolution,  # 媒体分辨率
                'video_dynamic_range': video_dynamic_range,  # 动态范围
                'rating': rating,  # 分数
                'stream_video_dynamic_range': stream_video_dynamic_range,  # 转码后动态范围
                'duration': duration,  # 总时长
                'datestamp': datestamp,  # 播放日期
                'product': product,  # 设备
                'player': player,  # 播放器
                'air_date': air_date,  # 出品日期
                'file_size': file_size,  # 文件大小
                'current_weekday': current_weekday,  # 星期几
                'remaining_duration': remaining_duration,  # 剩余时长
                'country': country,  # ip归属地(国)
                'city': city,  # ip归属地(市)
                'progress': progress,  # 进度条

            }

            _LOGGER.info('模板赋值')
            # 模板赋值
            wxtitledst = wxtitle.format(**qry)
            wxbodydst = wxbody.format(**qry)

            _LOGGER.info(wxtitledst)
            _LOGGER.info(wxbodydst)
            for uid in self.config.get('uid'):
                # 微信推送
                self.mrserver.notify.send_message_by_tmpl('{{title}}', '{{a}}', {
                    'title': wxtitledst,
                    'a': wxbodydst,
                    'link_url': artUrl,
                    'pic_url': artUrl

                }, uid,to_channel_name=self.config.get('ToChannelName'))


        except Exception as e:
            _LOGGER.error("{0} {1} 第{2}行".format(e,e.__traceback__.tb_frame.f_globals["__file__"],e.__traceback__.tb_lineno))

        # raise Exception(u'error')

    def on_play(self, event: PlaySessionStateNotification):
        # _LOGGER.info(f'on_play')
        self.player_event(event)

    def can_scrobble(self, event: PlaySessionStateNotification):
        if not self.username_filter:
            return True

        return self.sessions[event.session_key] == self.username_filter


class plexnotice:
    def __init__(self):
        self._flag = False
    def setflag(self,flag):
        self._flag = flag
    def process(self, config):
        from mbot.openapi import mbot_api
        from mbot.openapi import media_server_manager
        mrserver = mbot_api
        # get param
        try:
            _LOGGER.info(f'PlexNoticeStartListen!')
            servertype = "plex"
            if servertype == "plex":
                plex=media_server_manager.master_plex.plex
                ws = WebSocketListener(plex)
                # config=''
                updater = WatchStateUpdater(plex, config, mrserver)
                ws.on(
                    PlaySessionStateNotification,
                    updater.on_play,
                    state=["playing", "stopped", "paused"],
                )
                ws.on(
                    TimelineEntry,
                    updater.on_activity,
                    # type="library.refresh.items",
                    state=0,
                    # event="ended",
                    # progress=100,
                )
                ws.listen()
                _LOGGER.info(f'PlexNoticeStartListen!')
                while True:
                    if self._flag:
                        break
                    time.sleep(1)

        except Exception as e:
            _LOGGER.error("{0} {1} 第{2}行".format(e,e.__traceback__.tb_frame.f_globals["__file__"],e.__traceback__.tb_lineno))




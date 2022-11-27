
import logging

from mbot.external.mediaserver import MediaServerInstance
import sys
from moviebotapi import MovieBotServer
from moviebotapi.core.models import MediaType
from moviebotapi.core.session import AccessKeySession
from mbot.openapi import mbot_api
server = mbot_api
_LOGGER = logging.getLogger(__name__)


class plexchineseactor:
    def process_single(self,video):
        TypeDic={
            'show':MediaType.TV,
            'movie':MediaType.Movie
        }
        video.reload()
        _LOGGER.info(video.title)
        guids=video.guids
        # 获取tmdbid
        tmdbid=''
        for v in guids:
            if v.id.split("://")[0]== 'tmdb':
                tmdbid=v.id.split("://")[1]
        _LOGGER.info("获取演员信息")
        if video.TYPE=="show":
            data=server.meta.get_cast_crew_by_tmdb(TypeDic[video.TYPE], tmdbid,1)
        else:
            data=server.meta.get_cast_crew_by_tmdb(TypeDic[video.TYPE], tmdbid)
        _LOGGER.info("演员信息获取成功")
        ActorNum=0
        if data:
            roles=video.roles
            roleslist=[]
            for actor in video.roles:
                tag=actor.tag
                roleslist.append(tag)
            video.editTags(tag="actor", items=roleslist,remove=True)
            Num=min(len(data),10)
            if len(data)==0:
                print(video)
                pass
            for i in range(Num-1,0,-1):
                douban=data[i]
                if douban.duty=="Actor":
                    key={}
                    tag=douban.cn_name
                    locked=1
                    if douban.role =='':
                        text='演员'
                    else:
                        text=douban.role
                    
                    thumb=douban.douban_image_url

                    key["tag"]="actor["+str(ActorNum)+"].tag.tag"
                    key["locked"]="actor["+str(ActorNum)+"].locked'"
                    key["text"]="actor["+str(ActorNum)+"].tagging.text"
                    key["thumb"]="actor["+str(ActorNum)+"].tag.thumb"
                    edits = {
                        key["tag"]: tag,
                        key["locked"]: locked,
                        key["text"]: text,
                        key["thumb"]: thumb
                    }
                    video.edit(**edits)
                    ActorNum=ActorNum+1
        else:
            # print("error!")
            _LOGGER.error("获取到的中文演员信息为空! ")

    def process(self):
        servertype = MediaServerInstance.server_type
        if servertype == "plex":
            plex = MediaServerInstance.plex
            videos = plex.library.recentlyAdded()
            # print("开始处理近10个添加的媒体 ")
            _LOGGER.info("开始处理近10个添加的媒体")
            videoNum = 0
            for video in videos:
                videoNum = videoNum + 1
                if videoNum > 10:
                    break
                if video.type == "season":
                    parentkey = video.parentRatingKey
                    tvshows = plex.library.search(id=parentkey)
                    # plex.library.
                    # print(tvshows[0].title)
                    # _LOGGER.info(libtable[i])
                    self.process_single(tvshows[0])
                else:
                    print(video.title)
                    self.process_single(video)

    def process_all(self):
        servertype = MediaServerInstance.server_type
        if servertype == "plex":
            plex = MediaServerInstance.plex
            libtable=[]
            for section in plex.library.sections():
                if section.type == 'show' or section.type == 'movie':
                    print(section.title,section.key)
                    libtable.append(section.title)

            for i in range(len(libtable)):
                # print(libtable[i])
                _LOGGER.info(libtable[i])
                videos = plex.library.section(libtable[i])
                video_len=len(videos.all())
                for video,i in zip(videos.all(),range(video_len)):
                    self.process_single(video)

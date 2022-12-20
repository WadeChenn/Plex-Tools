
import logging



import sys
from moviebotapi import MovieBotServer
from moviebotapi.core.models import MediaType
from moviebotapi.core.session import AccessKeySession

_LOGGER = logging.getLogger(__name__)


class plexchineseactor:
    def __init__(self,server,plex,servertype='plex'):
        self.mrserver = server
        self.plex = plex
        self.servertype = servertype

    def process_single(self,video):
        TypeDic={
            'show':MediaType.TV,
            'movie':MediaType.Movie
        }
        roleslist = []
        # roleslist.append(video.roles[0].tag)

        # video.editTags(tag="roles", items=roleslist)
        # dstroleslist=[]
        # dstroleslist.append(roles[0])
        ActorNum = 0
        # video.reload()
        # video.editTags(tag="actor", items=roleslist, locked=False)
        # video.refresh()
        video.reload()
        _LOGGER.info(video.title)
        guids=video.guids
        # 获取tmdbid
        tmdbid=''
        for v in guids:
            if v.id.split("://")[0]== 'tmdb':
                tmdbid=v.id.split("://")[1]
        _LOGGER.info("Get Actors")
        if tmdbid != '':
            if video.TYPE=="show":
                data=self.mrserver.meta.get_cast_crew_by_tmdb(TypeDic[video.TYPE], tmdbid,1)
            else:
                data=self.mrserver.meta.get_cast_crew_by_tmdb(TypeDic[video.TYPE], tmdbid)
        else:
            return
        _LOGGER.info("Get Actors success")
        ActorNum=0
        rlist={
            'Actor':'演员',
            'Voice':'配音',
        }
        dstactors=[]
        if data:
            # roles=video.roles
            roleslist=[]
            for actor in video.actors:
                tag=actor.tag
                # roleslist.append(tag)
                dstactors.append(actor)
            mactors=[]
            for dstactor in dstactors:
                for douban in data:
                    if dstactor.tag == douban.en_name:
                        if douban.role !='' or dstactor.role !='':
                            if douban.role !='':
                                dstactor.role = douban.role
                            roleslist.append(dstactor.tag)
                            dstactor.tag = douban.cn_name
                            mactors.append(dstactor)


            # video.editTags(tag="actor", items=dstactors, locked=False)
            # pass
            Num=min(len(mactors),10)
            # if len(data)==0:
            #     print(video)
            #     pass
            video.editTags(tag="actor", items=roleslist, remove=True)
            for i in range(Num-1,-1,-1):
            # for dstactor in dstactors:
                dstactor=mactors[i]
                # if dstactor.duty=="Actor" or dstactor.duty=="Voice":
                key={}
                tag=dstactor.tag
                locked=False
                # if dstactor.role =='':
                #     text=rlist[dstactor.duty]
                # else:
                text=dstactor.role
                thumb=dstactor.thumb

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
    def get_library(self):
        if self.servertype == "plex":
            libtable = []
            lib = {}
            for section in self.plex.library.sections():
                _LOGGER.info(section.title)
                lib['name']=section.title
                lib['value']=section.title
                libtable.append(lib.copy())
            return libtable

    def refresh_single(self,video):
        roleslist = []
        # video.reload()
        video.editTags(tag="actor", items=roleslist, locked=False)
        video.refresh()
    def refreshmeta(self,library):
        if self.servertype == "plex":
            libtable=[]
            for section in self.plex.library.sections():
                if section.type == 'show' or section.type == 'movie':
                    if section.title in library:
                        print(section.title, section.key)
                        libtable.append(section.title)

            for i in range(len(libtable)):
                # print(libtable[i])
                _LOGGER.info(libtable[i])
                videos = self.plex.library.section(libtable[i])
                video_len=len(videos.all())
                for video,i in zip(videos.all(),range(video_len)):
                    self.refresh_single(video)

    def process(self):
        if self.servertype == "plex":
            videos = self.plex.library.recentlyAdded()
            # print("开始处理近10个添加的媒体 ")
            _LOGGER.info("开始处理近10个添加的媒体")
            videoNum = 0
            for video in videos:
                videoNum = videoNum + 1
                if videoNum > 10:
                    break
                if video.type == "season":
                    parentkey = video.parentRatingKey
                    tvshows = self.plex.library.search(id=parentkey)
                    # plex.library.
                    # print(tvshows[0].title)
                    # _LOGGER.info(libtable[i])
                    self.process_single(tvshows[0])
                else:
                    print(video.title)
                    self.process_single(video)

    def process_all(self,library):

        if self.servertype == "plex":
            libtable=[]
            for section in self.plex.library.sections():
                if section.type == 'show' or section.type == 'movie':
                    if section.title in library:
                        print(section.title, section.key)
                        libtable.append(section.title)

            for i in range(len(libtable)):
                # print(libtable[i])
                _LOGGER.info(libtable[i])
                videos = self.plex.library.section(libtable[i])
                video_len=len(videos.all())
                for video,i in zip(videos.all(),range(video_len)):
                    self.process_single(video)

import datetime
import os
import time
import logging
import requests
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz
from moviebotapi.core.models import MediaType
logging.basicConfig(level=logging.DEBUG)

# self.ACTIVITY_SCHED = None
_LOGGER = logging.getLogger(__name__)

class TimelineHandler(object):
    def __init__(self, timeline,plex,mrserver,config,RECENTLY_ADDED_QUEUE,ACTIVITY_SCHED):
        self.timeline = timeline
        self.plex=plex
        self.config=config
        self.mrserver = mrserver
        self.RECENTLY_ADDED_QUEUE= RECENTLY_ADDED_QUEUE
        self.ACTIVITY_SCHED=ACTIVITY_SCHED

    def is_item(self):
        if 'itemID' in self.timeline:
            return True

        return False

    def get_rating_key(self):
        if self.is_item():
            return int(self.timeline['itemID'])

        return None

    # def get_metadata(self):
    #     pms_connect = pmsconnect.PmsConnect()
    #     metadata = pms_connect.get_metadata_details(self.get_rating_key())
    #
    #     if metadata:
    #         return metadata
    #
    #     return None

    # This function receives events from our websocket connection
    def process(self):
        if self.is_item():
            MEDIA_TYPE_VALUES = {
                1: 'movie',
                2: 'show',
                3: 'season',
                4: 'episode',
                5: 'trailer',
                6: 'comic',
                7: 'person',
                8: 'artist',
                9: 'album',
                10: 'track',
                11: 'picture',
                12: 'clip',
                13: 'photo',
                14: 'photoalbum',
                15: 'playlist',
                16: 'playlistFolder',
                18: 'collection',
                42: 'optimizedVersion'
            }
            timeline = self.timeline
            # _LOGGER.info(vars(timeline))
            # testdata={'type': 'timeline', 'size': 1, 'TimelineEntry': [{'identifier': 'com.plexapp.plugins.library', 'sectionID': '8', 'itemID': '40010', 'type': 4, 'title': '斗罗大陆 S01 E235', 'state': 5, 'updatedAt': 1669339641}]}
            #{'identifier': 'com.plexapp.plugins.library', 'sectionID': '-1', 'itemID': '40120', 'type': 12, 'title': '', 'state': 0, 'metadataState': 'created', 'updatedAt': 1669619781}
            # self.plex.sear
            identifier = timeline.get('identifier')
            state_type = timeline.get('state')
            media_type = MEDIA_TYPE_VALUES.get(timeline.get('type'))
            section_id = int(timeline.get('sectionID', 0))
            title = timeline.get('title', 'Unknown')
            metadata_state = timeline.get('metadataState')
            media_state = timeline.get('mediaState')
            queue_size = timeline.get('queueSize')

            rating_key = timeline.get('itemID')


            if media_type and section_id > 0 and state_type == 0 and metadata_state == 'created':

                if media_type in ('episode', 'track'):
                    _LOGGER.info('media_type:'+media_type)

                    parent_rating_key = int(timeline.get('parentItemID')) or None
                    grandparent_rating_key = int(timeline.get('rootItemID')) or None
                    pass
                    grandparent_set = self.RECENTLY_ADDED_QUEUE.get(grandparent_rating_key, set())
                    grandparent_set.add(parent_rating_key)
                    self.RECENTLY_ADDED_QUEUE[grandparent_rating_key] = grandparent_set

                    parent_set = self.RECENTLY_ADDED_QUEUE.get(parent_rating_key, set())
                    parent_set.add(rating_key)
                    self.RECENTLY_ADDED_QUEUE[parent_rating_key] = parent_set

                    self.RECENTLY_ADDED_QUEUE[rating_key] = {grandparent_rating_key}
                    #test
                    # grandparent_set = self.RECENTLY_ADDED_QUEUE.get(grandparent_rating_key, set())
                    # grandparent_set.add(parent_rating_key)
                    # self.RECENTLY_ADDED_QUEUE[grandparent_rating_key] = grandparent_set
                    #
                    # parent_set = self.RECENTLY_ADDED_QUEUE.get(parent_rating_key, set())
                    # parent_set.add(rating_key)
                    # self.RECENTLY_ADDED_QUEUE[parent_rating_key] = parent_set
                    #
                    # self.RECENTLY_ADDED_QUEUE[rating_key] = {grandparent_rating_key}



                    _LOGGER.info("MR TimelineHandler :: Library item '%s' (%s, grandparent %s) "
                                  "added to recently added queue."
                                  % (title, str(rating_key), str(grandparent_rating_key)))

                    # self.clear_recently_added_queue(grandparent_rating_key, title,self.config,self.plex)

                    # Schedule a callback to clear the recently added queue
                    self.schedule_callback('rating_key-{}'.format(grandparent_rating_key),
                                      func=self.clear_recently_added_queue,
                                      args=[grandparent_rating_key, title,self.config,self.plex],
                                      seconds=int(self.config.get('Delay')))
                    pass
                #
                elif media_type in ('season', 'album'):
                    parent_rating_key = int(timeline.get('parentItemID')) or None
                    parent_set = self.RECENTLY_ADDED_QUEUE.get(parent_rating_key, set())
                    parent_set.add(rating_key)
                    self.RECENTLY_ADDED_QUEUE[parent_rating_key] = parent_set
                    #
                    _LOGGER.info("MR TimelineHandler :: Library item '%s' (%s , parent %s) "
                                  "added to recently added queue."
                                  % (title, str(rating_key), str(parent_rating_key)))
                    # self.clear_recently_added_queue(parent_rating_key, title,self.config,self.plex)

                #
                #     # Schedule a callback to clear the recently added queue
                    self.schedule_callback('rating_key-{}'.format(parent_rating_key),
                                      func=self.clear_recently_added_queue,
                                      args=[parent_rating_key, title,self.config,self.plex],
                                      seconds=int(self.config.get('Delay')))
                #
                elif media_type in ('movie', 'show', 'artist'):
                    queue_set = self.RECENTLY_ADDED_QUEUE.get(rating_key, set())
                    self.RECENTLY_ADDED_QUEUE[rating_key] = queue_set

                    _LOGGER.info("MR TimelineHandler :: Library item '%s' (%s) "
                                  "added to recently added queue."
                                  % (title, str(rating_key)))
                    # self.clear_recently_added_queue(rating_key, title,self.config,self.plex)

                #
                #     # Schedule a callback to clear the recently added queue
                    self.schedule_callback('rating_key-{}'.format(rating_key),
                                      func=self.clear_recently_added_queue,
                                      args=[rating_key, title,self.config,self.plex],
                                      seconds=int(self.config.get('Delay')))

                    # Schedule a callback to clear the recently added queue
                    self.schedule_callback('rating_key-{}'.format(rating_key),
                                      func=self.clear_recently_added_queue,
                                      args=[rating_key, title,self.config,self.plex],
                                      seconds=int(self.config.get('Delay')))

            # An item was deleted, make sure it is removed from the queue
            elif state_type == 9 and metadata_state == 'deleted':
                if rating_key in self.RECENTLY_ADDED_QUEUE and not self.RECENTLY_ADDED_QUEUE[rating_key]:
                    _LOGGER.info("MR TimelineHandler :: Library item %s "
                                 "removed from recently added queue."
                                 % str(rating_key))
                    self.del_keys(rating_key)

                    # Remove the callback if the item is removed
                    self.schedule_callback('rating_key-{}'.format(rating_key), remove_job=True)



    def del_keys(self,key):
        if isinstance(key, set):
            for child_key in key:
                self.del_keys(child_key)
        elif key in self.RECENTLY_ADDED_QUEUE:
            self.del_keys(self.RECENTLY_ADDED_QUEUE.pop(key))


    def schedule_callback(self,id, func=None, remove_job=False, args=None, **kwargs):

        if self.ACTIVITY_SCHED.get_job(id):
            if remove_job:
                self.ACTIVITY_SCHED.remove_job(id)
            else:
                self.ACTIVITY_SCHED.reschedule_job(
                    id, args=args, trigger=DateTrigger(
                        run_date=datetime.datetime.now(pytz.UTC) + datetime.timedelta(**kwargs),
                        timezone=pytz.UTC))
                # _LOGGER.info('添加任务成功 當前任務列表：{}'.format(self.ACTIVITY_SCHED.get_job(id)))

                # print('添加任务成功 當前任務列表：{}'.format(self.ACTIVITY_SCHED.get_job(id)))

                # self.ACTIVITY_SCHED.start()
        elif not remove_job:
            self.ACTIVITY_SCHED.add_job(
                func, args=args, id=id, trigger=DateTrigger(
                    run_date=datetime.datetime.now(pytz.UTC) + datetime.timedelta(**kwargs),
                    timezone=pytz.UTC),
                misfire_grace_time=None)
            self.ACTIVITY_SCHED.start()
            _LOGGER.info('生成新任务成功 當前任務列表：{}'.format(self.ACTIVITY_SCHED.get_jobs()))


    # def force_stop_stream(session_key, title, user):
    #     ap = activity_processor.ActivityProcessor()
    #     session = ap.get_session_by_key(session_key=session_key)
    #
    #     row_id = ap.write_session_history(session=session)
    #
    #     if row_id:
    #         plexpy.NOTIFY_QUEUE.put({'stream_data': session.copy(), 'notify_action': 'on_stop'})
    #
    #         # If session is written to the database successfully, remove the session from the session table
    #         _LOGGER.info("MR ActivityHandler :: Removing stale stream with sessionKey %s ratingKey %s from session queue"
    #                     % (session['session_key'], session['rating_key']))
    #         ap.delete_session(row_id=row_id)
    #         delete_metadata_cache(session_key)
    #
    #     else:
    #         session['write_attempts'] += 1
    #
    #         if session['write_attempts'] < plexpy.CONFIG.SESSION_DB_WRITE_ATTEMPTS:
    #             _LOGGER.warn("MR ActivityHandler :: Failed to write stream with sessionKey %s ratingKey %s to the database. " \
    #                         "Will try again in 30 seconds. Write attempt %s."
    #                         % (session['session_key'], session['rating_key'], str(session['write_attempts'])))
    #             ap.increment_write_attempts(session_key=session_key)
    #
    #             # Reschedule for 30 seconds later
    #             schedule_callback('session_key-{}'.format(session_key), func=force_stop_stream,
    #                               args=[session_key, session['full_title'], session['user']], seconds=30)
    #
    #         else:
    #             _LOGGER.warn("MR ActivityHandler :: Failed to write stream with sessionKey %s ratingKey %s to the database. " \
    #                         "Removing session from the database. Write attempt %s."
    #                         % (session['session_key'], session['rating_key'], str(session['write_attempts'])))
    #             _LOGGER.info("MR ActivityHandler :: Removing stale stream with sessionKey %s ratingKey %s from session queue"
    #                         % (session['session_key'], session['rating_key']))
    #             ap.delete_session(session_key=session_key)
    #             delete_metadata_cache(session_key)


    def clear_recently_added_queue(self,rating_key, title,config,plex):
        _LOGGER.debug("MR TimelineHandler :: Starting callback for library item '%s' (%s) after delay.",
                     title, str(rating_key))

        child_keys = self.RECENTLY_ADDED_QUEUE[rating_key]

        if config.get('NOTIFY_GROUP_RECENTLY_ADDED_GRANDPARENT') and len(child_keys) > 1:
            _LOGGER.debug("MR TimelineHandler :: Library item '%s' (%s) has %s children. "
                            "Notifying group recently added.",
                            title, str(rating_key), str(len(child_keys)))
            self.on_created(rating_key, child_keys=child_keys,plex=plex)

        elif child_keys:
            # _LOGGER.debug("MR TimelineHandler :: Library item '%s' (%s) has %s children. "
            #                 "Notifying recently added for each child.elif child_keys:",
            #                 title, str(rating_key), str(len(child_keys)))
            # _LOGGER.debug("child_keys")
            for child_key in child_keys:
                grandchild_keys = self.RECENTLY_ADDED_QUEUE.get(child_key, [])

                if config.get('NOTIFY_GROUP_RECENTLY_ADDED_PARENT') and len(grandchild_keys) > 1:
                    _LOGGER.debug("grandchild_keys >1")
                    self.on_created(child_key, child_keys=grandchild_keys,plex=plex)

                elif grandchild_keys:
                    # _LOGGER.info("grandchild_keys >1")
                    for grandchild_key in grandchild_keys:
                        self.on_created(grandchild_key,plex=plex)

                else:
                    self.on_created(child_key,plex=plex)

        else:
            self.on_created(rating_key,plex=plex)

        # Remove all keys
        self.del_keys(rating_key)


    def on_created(self,rating_key,plex, **kwargs):
        # pms_connect = pmsconnect.PmsConnect()
        # plex=plex
        self.mrserver.event.publish_event('PlexActivityEvent', {
            'Activity': 'Added'
        })
        metadata = self.get_metadata_details(plex,rating_key)
        _LOGGER.debug("MR  TimelineHandler :: Library item '%s' (%s) added to Plex.",
                     metadata['full_title'], str(rating_key))

        if metadata:
            notify = True
            # now = helpers.timestamp()
            #
            # if int(metadata['added_at']) < now - 86400:  # Updated more than 24 hours ago
            #     _LOGGER.info("MR TimelineHandler :: Library item %s added more than 24 hours ago. Not notifying."
            #                  % str(rating_key))
            #     notify = False

            # data_factory = datafactory.DataFactory()
            # if 'child_keys' not in kwargs:
            #     if data_factory.get_recently_added_item(rating_key):
            #         _LOGGER.info("MR TimelineHandler :: Library item %s added already. Not notifying again."
            #                      % str(rating_key))
            #         notify = False
            # metadata['artUrl'] = video[0].artUrl
            # metadata['thumbUrl'] = video[0].thumb
            # metadata['library'] = video[0].librarySectionTitle
            # metadata['added_at'] = video[0].addedAt
            # now = datetime.datetime.now()
            # current_weekday = week[now.weekday()]
            # timestamp = '{0:0>2d}:{1:0>2d}:{2:0>2d}'.format(now.hour, now.minute,
            #                                                 now.second)
            # datestamp = '{0}-{1:0>2d}-{2:0>2d}'.format(now.year, now.month,
            #                                            now.day)
            # metadata['current_weekday'] = current_weekday
            # metadata['timestamp'] = timestamp
            # metadata['datestamp'] = datestamp
            subtitle=''
            if notify:
                data = {'timeline_data': metadata, 'notify_action': 'on_created'}
                data.update(kwargs)
                print(data)
                # _LOGGER.info('模板赋值')
                indexmin = 0
                indexmax = 0
                for child_key in kwargs.get('child_keys', []):

                    child=self.get_metadata_details(plex,child_key)
                    if indexmin==0:
                        indexmin=child.get('index')
                    indexmin= min(child.get('index'),indexmin)
                    indexmax= max(child.get('index'),indexmax)
                        # episodemax = child.get('index')
                        # seasonmin = child.get('parent_index')
                        # seasonmax = child.get('parent_index')
                if indexmin != indexmax:
                #     subtitle = '第'+str(indexmin)+'集'
                # else:
                #     subtitle = '第'+str(indexmin)+'-'+str(indexmax)+'集'
                # if metadata.get('type') == 'episode':
                #     metadata['subtitle'] = subtitle
                    if metadata.get("type") == 'season':
                        metadata['full_title'] = metadata['full_title'].replace('Season ','S')
                        subtitle=' E{0:0>2d}-{1:0>2d}'.format(indexmin,indexmax)
                    elif metadata.get("type") == 'show':
                        subtitle='S{0:0>2d}-S{1:0>2d}'.format(indexmin,indexmax)
                qry = {
                    'title': metadata.get('full_title')+subtitle,
                    'artUrl': metadata.get('artUrl'),
                    'library_name': metadata.get('library'),
                    'thumbUrl': metadata.get('thumbUrl'),
                    'added_at': metadata.get('added_at'),
                    'current_weekday': metadata.get('current_weekday'),
                    'timestamp': metadata.get('timestamp'),
                    'datestamp': metadata.get('datestamp'),
                    'summary': metadata.get('summary'),
                    'subtitle': metadata.get('subTitle'),

                }
                # 模板赋值

                temp = {
                    'title': self.config.get('AddTitle'),
                    'body': self.config.get('Add')
                }
                wxtitle = temp.get('title')
                wxbody = temp.get('body')
                wxtitledst = wxtitle.format(**qry)
                wxbodydst = wxbody.format(**qry)
                wxbodydst=wxbodydst.replace('\n\n','\n')
                _LOGGER.info(wxtitledst)
                _LOGGER.info(wxbodydst)
                channel_table = self.config.get('ToChannelName').split(',')
                uid_table = self.config.get('uid')
                if uid_table: # 判断uid是否为空
                    for channel in channel_table:
                        for uid in self.config.get('uid'):
                            # 微信推送
                            self.mrserver.notify.send_message_by_tmpl('{{title}}', '{{a}}', {
                                'title': wxtitledst,
                                'a': wxbodydst,
                                'link_url': metadata.get('artUrl'),
                                'pic_url': metadata.get('artUrl')
                            }, uid,to_channel_name=channel)

                else:
                    for channel in channel_table:
                        # 微信推送
                        self.mrserver.notify.send_message_by_tmpl('{{title}}', '{{a}}', {
                            'title': wxtitledst,
                            'a': wxbodydst,
                            'link_url': metadata.get('artUrl'),
                            'pic_url': metadata.get('artUrl')
                        },to_channel_name=channel)
                # plexpy.NOTIFY_QUEUE.put(data)

            all_keys = [rating_key]
            if 'child_keys' in kwargs:
                all_keys.extend(kwargs['child_keys'])

            # for key in all_keys:
            #     data_factory.set_recently_added_item(key)

            _LOGGER.info("Added %s items to the recently_added database table." % str(len(all_keys)))

        else:
            _LOGGER.error("MR TimelineHandler :: Unable to retrieve metadata for rating_key %s" % str(rating_key))

    def get_metadata_details(self,plex,rating_key):
        week = {
            0: "一",
            1: "二",
            2: "三",
            3: "四",
            4: "五",
            5: "六",
            6: "日",
        }
        video = plex.library.search(id=rating_key)
        metadata = {}
        metadata['subTitle'] = ''
        metadata['summary']=''
        tmdb_id=0
        media_type = MediaType.Movie
        section=video
        if video[0].type=='season':
            metadata['full_title']='{} {}'.format(video[0].parentTitle,video[0].title)
            metadata['summary'] = video[0].summary
            metadata['index'] = video[0].index
            section = plex.library.search(id=video[0].parentRatingKey)
            media_type = MediaType.TV
        if video[0].type=='movie':
            metadata['full_title']='{}'.format(video[0].title)
            metadata['summary'] = video[0].summary
            media_type = MediaType.Movie

        if video[0].type=='show':
            metadata['full_title']='{}'.format(video[0].title)
            # metadata['seasonNumber'] = video[0].seasonNumber
            metadata['index'] = video[0].index
            metadata['summary'] = video[0].summary
            media_type = MediaType.TV
        if video[0].type == 'episode':
            metadata['full_title'] = '{} {}'.format(video[0].grandparentTitle, video[0].seasonEpisode.upper().replace('E', '·E'))
            metadata['subTitle'] = '\n单集标题:'+video[0].title
            metadata['episodeNumber'] = video[0].episodeNumber
            metadata['index'] = video[0].index
            section = plex.library.search(id=video[0].grandparentRatingKey)
            media_type = MediaType.TV
        for id in section[0].guids:
            if id.id.split('://')[0] == 'tmdb':
                tmdb_id = id.id.split('//')[1]
        artUrl=''
        metadata['type']=video[0].TYPE
        # artUrl = video[0].artUrl
        # _LOGGER.info('UseTMDB')
        # if self.config.get('UseTMDB') and tmdb_id != '':
        #     tmdbinfo = self.mrserver.tmdb.get(media_type, tmdb_id)
        #     if tmdbinfo.backdrop_path:
        #         artUrl = 'https://image.tmdb.org/t/p/w500' + tmdbinfo.backdrop_path
        #     else:
        #         artUrl = 'https://s2.loli.net/2022/11/28/P68gBzJ7fnRVO3Z.png'
        # elif self.config.get('PlexUrl') != 'ispublic':
        #     if artUrl != None:
        #         token = section.artUrl.split('Plex-Token=')[1]
        #         artUrl = self.config.get('PlexUrl') + art + '?X-Plex-Token=' + token
        #     else:
        #         artUrl = 'https://s2.loli.net/2022/11/28/P68gBzJ7fnRVO3Z.png'
        if section[0].posterUrl and section[0].art:
            token = section[0].posterUrl.split('Plex-Token=')[1]
            artUrl = self.config.get('PlexUrl') + section[0].art + '?X-Plex-Token=' + token
        else:
            if  tmdb_id != '':
                tmdbinfo = self.mrserver.tmdb.get(media_type, tmdb_id)
                if tmdbinfo and tmdbinfo.backdrop_path:
                    artUrl = 'https://image.tmdb.org/t/p/w500' + tmdbinfo.backdrop_path
        # artUrl = self.config.get('PlexUrl') + section[0].art + '?X-Plex-Token=' + token

        metadata['artUrl']=artUrl
        metadata['thumbUrl']=video[0].thumb
        metadata['library']=video[0].librarySectionTitle
        metadata['added_at']=video[0].addedAt
        now = datetime.datetime.now()
        current_weekday = week[now.weekday()]
        timestamp = '{0:0>2d}:{1:0>2d}:{2:0>2d}'.format(now.hour, now.minute,
                                                        now.second)
        datestamp = '{0}-{1:0>2d}-{2:0>2d}'.format(now.year, now.month,
                                                   now.day)
        metadata['current_weekday'] = current_weekday
        metadata['timestamp'] = timestamp
        metadata['datestamp'] = datestamp
        #判断字符串是否是中文

        #删除字符串空格
        if metadata.get('summary') != '':
            if is_chinese(metadata.get('summary').replace(' ', '').replace(':', '').replace('　','')[4]) :
                metadata['summary'] = metadata.get('summary').replace(' ', '').replace('　','')
            metadata['summary'] = '\n简介:' + metadata['summary']







        # metadata['year']=video[0].year

        return metadata
        # _LOGGER.info(movie)

    # def delete_metadata_cache(self,session_key):
    #     try:
    #         os.remove(os.path.join(plexpy.CONFIG.CACHE_DIR, 'session_metadata/metadata-sessionKey-%s.json' % session_key))
    #     except OSError as e:
    #         _LOGGER.error("MR ActivityHandler :: Failed to remove metadata cache file (sessionKey %s): %s"
    #                      % (session_key, e))

def is_chinese(uchar):
    if '\u4e00' <= uchar <= '\u9fa5':
        return True
    else:
        return False
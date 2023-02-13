import logging
import time

import sys
from moviebotapi.core.models import MediaType

RECOVER = 1
ENABLE_LOG = 1
_LOGGER = logging.getLogger(__name__)

import re
media_output = {}

class plexautoskip:
    def __init__(self):
        self._flag = False
    def setflag(self,flag):
        self._flag = flag
    def setdata(self,plex,mrserver,servertype):
        self.plexserver = plex
        self.mrserver = mrserver
        self.servertype = servertype
    def setconfig(self,config):
        self.config = config

    def move(self,player, time):
        # move stream to end of chapter/marker
        minutes = time / 1000 / 60
        seconds = int(minutes % 1 * 60)
        minutes = int(minutes)
        logging.info(f'Moving stream playing on {player} to {minutes}:{seconds}')
        try:
            self.plexserver.client(player).seekTo(time, mtype='video')
            logging.info('Success')
        except Exception as e:
            logging.exception('Failed: ')
        return

    def chapter_check(self,data, rating_key, player):
        # check if stream is currently in chapter that needs to be skipped
        if media_output[rating_key].chapters:
            for chapter in media_output[rating_key].chapters:
                if not chapter.tag: continue
                if (self.config.get("Intro") == True and chapter.tag.lower() == 'intro') or (
                        self.config.get("Outro") == True and chapter.tag.lower() == 'outro') or (
                        self.config.get("Advertisements") == True and chapter.tag.lower() in (
                        'ad', 'ads', 'advertisement', 'advertisements')):
                    if chapter.start <= data['viewOffset'] <= chapter.end:
                        # current chapter needs to be skipped
                        self.move(player, chapter.end)
                        return 'Moved'
        return 'Not-Moved'

    def marker_check(self,data, rating_key, player):
        # check if stream is currently in marker that needs to be skipped

        if media_output[rating_key].markers:
            for marker in media_output[rating_key].markers:
                if not marker.type: continue
                if (self.config.get("Intro") == True and marker.type.lower() == 'intro') or (
                        self.config.get("Outro") == True and marker.type.lower() == 'outro') or (
                        self.config.get("Advertisements") == True and marker.type.lower() in (
                        'ad', 'ads', 'advertisement', 'advertisements')):
                    if marker.start <= data['viewOffset'] <= marker.end:
                        # current marked area needs to be skipped
                        self.move(player, marker.end)
                        return 'Moved'
        return 'Not-Moved'

    def process(self,data):
        if data['type'] == 'playing':
            logging.debug(data)
            data = data['PlaySessionStateNotification'][0]
            rating_key = str(data['ratingKey'])
            sessions = self.plexserver.sessions()

            for session in sessions:

                logging.debug(session)
                if str(session.sessionKey) == str(data['sessionKey']):
                    media_output[rating_key] = self.plexserver.library.fetchItem(int(rating_key))

                    if not session.locate == 'lan':return

                    #
                    #
                    # logging.debug(media_output[rating_key])

                    # check for chapters and skip if needed
                    if self.chapter_check(data, rating_key, session.players[0].title) == 'Moved': return
                    self.marker_check(data, rating_key, session.players[0].title)
                    return
            else:
                logging.error('Not able to find session back in status')
                return

    def start(self):
        try:
            listener = self.plexserver.startAlertListener(callback=self.process)
            while True:
                if self._flag:
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info('Shutting down')
            listener.stop()
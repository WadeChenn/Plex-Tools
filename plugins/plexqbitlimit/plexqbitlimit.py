
import logging
from moviebotapi.core.models import MediaType
_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
import os
import qbittorrentapi

class plexqbitlimit:
    def __init__(self):
        pass
    def setdata(self,plex,mrserver,servertype):

        self.plexserver = plex
        self.mrserver = mrserver
        self.servertype = servertype

    # def get_library(self):
    #     if self.servertype == "plex":
    #         libtable = []
    #         lib = {}
    #         for section in self.plexserver.library.sections():
    #             _LOGGER.info(section.title)
    #             lib['name']=section.title
    #             lib['value']=section.title
    #             libtable.append(lib.copy())
    #         return libtable
    def process(self,config):
        try:
            if self.servertype == "plex":
                _LOGGER.info("开始处理")
                needlimit = False
                ineraddress = {"127", "10", "192"}
                qbt_client = qbittorrentapi.Client(
                    host=config.get('QBIT_URL'),
                    port=config.get('QBIT_PORT'),
                    username=config.get('QBIT_MAME'),
                    password=config.get('QBIT_PASSWORD')
                )

                try:
                    qbt_client.auth_log_in()
                    print('Qbit 登入成功')
                except qbittorrentapi.LoginFailed as e:
                    print(e)
                    print("Qbit 登入失败!")

                sessions = self.plexserver.sessions()
                bandwidth = 0
                for session in sessions:
                    if session.TYPE == 'track':
                        continue
                    for player in session.players:
                        address = player.address.split('.')[0]
                        if address not in ineraddress and player.state != 'paused':
                            for s in session.session:
                                bandwidth = bandwidth + s.bandwidth / 1024 / 8
                            needlimit = True
                SPEEDLIMIT = (config.get('NET_BANDWIDTH') - bandwidth) * 1024 * 1024
                # COMMAND="test"
                if needlimit:
                    if config.get('MODE'):
                        print("有【 {count} 】个设备正在活动，其中含有外网正在播放的设备，Qbit开始切换为备用限速".format(
                            count=len(sessions)))
                        qbt_client.transfer.speed_limits_mode = True
                    else:
                        if round(SPEEDLIMIT / 1024 / 1024, 1) > 0:
                            print(
                                "有【 {count} 】个设备正在活动，其中含有外网正在播放的设备，Qbit开始限速：【 {speedlimit} MiB/s 】".format(
                                    count=len(sessions), speedlimit=round(SPEEDLIMIT / 1024 / 1024, 1)))
                            qbt_client.transfer_set_upload_limit(limit=int(SPEEDLIMIT))
                        else:
                            print(
                                "有【 {count} 】个设备正在活动，其中含有外网正在播放的设备，影片所需带宽超过宽带上限，Qbit不限速".format(
                                    count=len(sessions)))
                            qbt_client.transfer_set_upload_limit(limit=0)
                else:
                    print("外网没有设备在播放，Qbit不限速")
                    # print("Executing command: {cmd}".format(cmd=COMMAND))
                    if config.get('MODE'):
                        qbt_client.transfer.speed_limits_mode = False
                    else:
                        qbt_client.transfer_set_upload_limit(limit=0)
        except Exception as e:
            print(e)
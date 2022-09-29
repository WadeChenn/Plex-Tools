###################################### 所有脚本参数配置 ###############################

################################## 拼音排序+汉化标签 ##################################
USE_INIT=False                      #使用当前配置请设为True,否则False将尝试从外部获取参数
PLEX_TOKEN="zZzxxxxxxxJssiw2zcy"    #Plextoken获取,具体方法请自行查找 "zZzxxxxxxxJssiw2zcy" *必须设置
PLEX_URL="http://plex.xxx.cn:32400" #Plexurl "http://plex.xxx.cn:32400" （也可填内网地址） *必须设置
RECOVER=False                       #是否覆盖已有的拼音排序
LIB_NAME=''                         #要排序的库名(存在时库编号不生效)
LIB_NUMBER=0                        #要排序的库编号(不使用库编号则设为0)
ENABLE_LOG=1                        #是否输出进度条
MEDIA_ID=0
###############################QBIT######################################
QBIT_URL="http://qbit.***.com"
QBIT_PORT=8082
QBIT_MAME='admin'
QBIT_PASSWORD='adminadmin'
SPEEDLIMIT=1000                              #单位为kb
MODE=0                                       #限速模式 0:切换备用速度 1:直接限制速度为SPEEDLIMIT

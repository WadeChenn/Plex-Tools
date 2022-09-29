# Qbit_upload_limit
## 功能介绍
- [x] 通过检测 Plex 播放状态，有外网设备正在播放时，对 Qbit 进行上传限速,内网设备播放不限速

#### 支持类型  
✅ 电影    ✅ 剧集

## 配合 Tautulli 使用
### 方法
- Qbit WEB页面中设置备用上传限速
- 将`qbit_upload_limit.py`文件放入 tautulli 的`/config/script/`目录下，`config.py`填入相关配置，
- Tautulli 中新建通知-类型选-script
- 选择 `qbit_upload_limit.py`
- Tautulli 触发条件勾选，`播放` `停止` `暂停` `恢复播放`
- 保存即可（当外网有设置正在播放时，自动对 Qbit 进行上传限速）

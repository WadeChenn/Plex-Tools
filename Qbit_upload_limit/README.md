# Qbit_upload_limit
## 注意 脚本会自动安装所需要模块，qbitapi模块存在无安装权限问题 需要手动进去tautulli终端内安装 pip3 install qbittorrent-api

## 功能介绍
- [x] 通过检测 Plex 播放状态，有外网设备正在播放时，对 Qbit 进行上传限速,内网设备播放不限速
- [x] 配合 Tautulli 使用，在 `开始` `暂停` `恢复` `停止`时触发脚本即可，无需参数传入

#### 支持类型  
✅ 电影    ✅ 剧集

## 配合 Tautulli 使用
### 方法
- Qbit WEB页面中设置备用上传限速
- 将`qbit_upload_limit.py` `config.py` 文件放入 tautulli 的`/config/script/`目录下，`config.py`填入相关配置，
- Tautulli 中新建通知-类型选-script
- 选择 `qbit_upload_limit.py`
- Tautulli 触发条件勾选，`播放` `停止` `暂停` `恢复播放`
- 保存即可（当外网有设置正在播放时，自动对 Qbit 进行上传限速）
## 主要配置截图
![image](https://user-images.githubusercontent.com/68833595/193017070-d83aa480-c74a-4186-a85d-d5fc5e1bae77.png)
![image](https://user-images.githubusercontent.com/68833595/193017373-e6d071c9-0e94-4945-8991-d7b0cf5f05f3.png)
![image](https://user-images.githubusercontent.com/68833595/193017100-3edcded6-bfdf-40ab-bc2f-57d05300ff6d.png)


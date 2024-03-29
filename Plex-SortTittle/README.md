# Plex-SortTittle
## 功能介绍
- [x] 修改Plex排序名称为拼音,以便于进行中文影音的搜索及排序 
- [x] 整理影片标签,将英文标签转换为中文标签 (配合tautulli，影片入库时自动运行)
- [x] 自动打标签,自动识别豆瓣/IMDBTOP250影片自动添加标签 方便分类查询 (配合tautulli，影片入库时自动运行)

>脚本为Python3 编写,需要安装python3环境,脚本中会自动安装所需依赖包  
群晖默认无python3 及pip环境 可参考 [此链接配置](https://www.notion.so/0bm/pip3-073e2ec6874b4f7aa65502f573343312)

#### 支持类型  
✅ 电影    ✅ 剧集    ✅ 音乐 

## 效果预览
<div align=center><img src="https://user-images.githubusercontent.com/68833595/192448307-328c46e2-1f21-48dd-97c6-89c442b0f3ec.png" width="1000" /></div>
<div align=center><img src="https://user-images.githubusercontent.com/68833595/192448056-183f5cec-6e94-498f-955b-b6518b56835e.png" width="1000" /></div>

## 脚本使用方式
1. 外部传参
2. 脚本内部配置参数(将 `USE_INIT` 设为 `True`)
3. 直接运行(会提示输入选择要排序的库)，运行命令 `python SortTittle.py`

## 配合 Tautulli 使用 - 外部传参
配合tautulli，影片入库时自动运行，
### 方法 
- 将`SortTittle.py` `config.py`文件放入 tautulli 的 `/config/script/` 目录下，`config.py`填入相关配置
- Tautulli 中新建通知-类型选-script
- 选择 `SortTittle.py`
- Triggers tab页勾选 `Recently Added`
- Arguments tab页在 `Recently Added` 中填入下方代码
- 保存即可（当有新影片入库，自动执行脚本）
```console
-mid 1
```
<img width="1022" alt="image" src="https://user-images.githubusercontent.com/68833595/199144554-2f0afc9f-8f0a-4b70-aace-b70116d29c23.png">

## TODO list
- [ ] 添加集合排序规则修改

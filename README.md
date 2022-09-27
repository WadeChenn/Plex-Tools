# Plex-SortTittle
Plex-SortTittle
当前脚本修改Plex排序名称为拼音,以便于进行中文影音的搜索及排序  
新版可支持整理剧集标签,将英文标签转换为中文标签 (整理库时自动运行)

>脚本为Python3 编写,需要安装python3环境,脚本中会自动安装所需依赖包  
群晖默认无python3 及pip环境 可参考 [此链接配置](https://www.notion.so/0bm/pip3-073e2ec6874b4f7aa65502f573343312)

#### 支持类型  
✅ 电影    ✅ 剧集    ✅ 音乐 

## 效果预览
<img width="1063" alt="image" src="https://user-images.githubusercontent.com/68833595/192448307-328c46e2-1f21-48dd-97c6-89c442b0f3ec.png">

<img width="1074" alt="image" src="https://user-images.githubusercontent.com/68833595/192448056-183f5cec-6e94-498f-955b-b6518b56835e.png">
 
## 脚本使用方式
1. 外部传参
2. 脚本内部配置参数(将 `USE_INIT` 设为 `True`)
3. 直接运行(会提示输入选择要排序的库)，运行命令 `python SortTittle.py`

## 配合 Tautulli 使用 - 外部传参
### 方法
- 将`SortTittle.py`文件放入 tautulli 的/config/script/目录下，`SortTittle.py`填入相关配置，将 `USE_INIT` 设为`False`
- Tautulli 中新建通知-类型选-script
- 选择 `SortTittle.py`
- 入库处填入下方通知代码
- 保存即可（当有新影片入库，自动执行脚本）
```console
<movie>-mid {rating_key}</movie><show>-mid {grandparent_rating_key}</show><season>-mid {parent_rating_key}</season>
```
<div align=center><img src="https://user-images.githubusercontent.com/68833595/192447181-58b6f04d-feab-4eba-943f-bc19dfa9c2c1.png" width="1000" /></div>


## TODO list
- [ ] 添加集合排序规则修改

import logging

from mbot.external.mediaserver import MediaServerInstance
import sys

RECOVER = 1
ENABLE_LOG = 1
_LOGGER = logging.getLogger(__name__)

import pypinyin
import re

IMDBTop250 = {'肖申克的救赎', '教父', '教父2', '蝙蝠侠：黑暗骑士', '十二怒汉', '辛德勒的名单', '指环王3：国王归来',
              '低俗小说', '黄金三镖客', '指环王1：魔戒现身', '搏击俱乐部', '阿甘正传', '盗梦空间', '指环王2：双塔奇兵',
              '星球大战2：帝国反击战', '黑客帝国', '好家伙', '飞越疯人院', '七武士', '七宗罪', '美丽人生', '上帝之城',
              '沉默的羔羊', '生活多美好', '星球大战', '拯救大兵瑞恩', '绿里奇迹', '千与千寻', '星际穿越', '寄生虫',
              '这个杀手不太冷', '切腹', '非常嫌疑犯', '狮子王', '钢琴家', '回到未来', '终结者2', '美国X档案',
              '摩登时代', '角斗士', '惊魂记', '无间行者', '城市之光', '触不可及', '爆裂鼓手', '萤火虫之墓', '致命魔术',
              '西部往事', '卡萨布兰卡', '天堂电影院', '后窗', '异形', '现代启示录', '记忆碎片', '大独裁者', '夺宝奇兵',
              '被解救的姜戈', '汉密尔顿', '窃听风暴', '光荣之路', '小丑', '机器人总动员', '闪灵',
              '复仇者联盟3：无限战争', '日落大道', '控方证人', '老男孩', '蜘蛛侠：平行宇宙', '幽灵公主', '奇爱博士',
              '蝙蝠侠：黑暗骑士崛起', '美国往事', '你的名字', '异形2', '寻梦环游记', '复仇者联盟4：终局之战', '美国美人',
              '何以为家', '勇敢的心', '从海底出击', '玩具总动员', '三傻大闹宝莱坞', '天国与地狱', '莫扎特传',
              '无耻混蛋', '星球大战3：绝地归来', '心灵捕手', '地球上的星星', '落水狗', '2001太空漫游', '梦之安魂曲',
              '迷魂记', 'M就是凶手', '狩猎', '美丽心灵的永恒阳光', '公民凯恩', '摔跤吧！爸爸', '雨中曲', '偷自行车的人',
              '全金属外壳', '寻子遇仙记', '自己去看', '偷拐抢骗', '西北偏北', '发条橙子', '疤面煞星', '生之欲', '1917',
              '出租车司机', '焦土之城', '一次别离', '阿拉伯的劳伦斯', '玩具总动员3', '骗中骗', '天使爱美丽', '大都会',
              '桃色公寓', '黄昏双镖客', '双重赔偿', '杀死一只知更鸟', '飞屋环游记', '夺宝奇兵3', '盗火线', '洛城机密',
              '虎胆龙威', '绿皮书', '巨蟒与圣杯', '蝙蝠侠：侠影之谜', '用心棒', '罗生门', '帝国的毁灭', '小鞋子',
              '不可饶恕', '乱', '热情似火', '哈尔的移动城堡', '彗星美人', '赌城风云', '美丽心灵', '华尔街之狼',
              '大逃亡', '潘神的迷宫', '谜一样的双眼', '血色将至', '两杆大烟枪', '纽伦堡大审判', '龙猫', '愤怒的公牛',
              '碧血金沙', '电话谋杀案', '三块广告牌', '禁闭岛', '淘金记', '唐人街', '我的父亲，我的儿子', '老无所依',
              'V字仇杀队', '头脑特工队', '象人', '怪形', '第七封印', '勇士', '灵异第六感', '猜火车', '侏罗纪公园',
              '克劳斯：圣诞节的秘密', '楚门的世界', '乱世佳人', '海底总动员', '潜行者', '野草莓', '银翼杀手', '杀死比尔',
              '杀人回忆', '恶魔', '桂河大桥', '冰血暴', '房间', '荒蛮故事', '老爷车', '第三人', '东京物语', '码头风云',
              '猎鹿人', '因父之名', '玛丽和马克思', '布达佩斯大饭店', '爱在黎明破晓前', '消失的爱人', '猫鼠游戏',
              '血战钢锯岭', '快乐的阿南', '囚徒', '假面', '调音师', '福尔摩斯二世', '谋杀绿脚趾', '秋日奏鸣曲',
              '你逃我也逃', '将军号', '乱世儿女', '驯龙高手', '极速车王', '强盗', '为奴十二年', '史密斯先生到华盛顿',
              '疯狂的麦克斯4：狂暴之路', '死亡诗社', '百万美元宝贝', '电视台风云', '伴我同行', '哈利·波特与死亡圣器(下)',
              '宾虚', '忠犬八公的故事', '心灵奇旅', '铁窗喋血', '小姐', '野战排', '金刚狼3：殊死一战', '荒野生存',
              '极速风流', '恐惧的代价', '万世魔星', '怒火青春', '四百击', '圣女贞德蒙难记', '聚焦', '卢旺达饭店',
              '爱情是狗娘', '瓦塞浦黑帮', '安德烈·卢布廖夫', '洛奇', '怪兽电力公司', '风之谷', '流浪者之歌', '蝴蝶梦',
              '爱在日落黄昏时', '芭萨提的颜色', '男人的争斗', '花样年华', '德州巴黎', '一夜风流', '燃烧女子的肖像',
              '误杀瞒天记', '较量', '声之形', '看不见的客人', '阿尔及尔之战', '帮助', '故土'}
DouBanTop250 = {'肖申克的救赎', '霸王别姬', '阿甘正传', '泰坦尼克号', '这个杀手不太冷', '美丽人生', '千与千寻',
                '辛德勒的名单', '盗梦空间', '星际穿越', '忠犬八公的故事', '楚门的世界', '海上钢琴师', '三傻大闹宝莱坞',
                '机器人总动员', '放牛班的春天', '无间道', '疯狂动物城', '大话西游之大圣娶亲', '控方证人', '熔炉',
                '教父', '当幸福来敲门', '触不可及', '怦然心动', '龙猫', '末代皇帝', '寻梦环游记', '蝙蝠侠：黑暗骑士',
                '活着', '哈利·波特与魔法石', '指环王3：王者无敌', '乱世佳人', '素媛', '飞屋环游记', '我不是药神',
                '摔跤吧！爸爸', '何以为家', '十二怒汉', '哈尔的移动城堡', '鬼子来了', '少年派的奇幻漂流', '猫鼠游戏',
                '让子弹飞', '大话西游之月光宝盒', '天空之城', '钢琴家', '海蒂和爷爷', '指环王2：双塔奇兵', '闻香识女人',
                '天堂电影院', '罗马假日', '大闹天宫', '指环王1：护戒使者', '黑客帝国', '死亡诗社', '绿皮书', '教父2',
                '狮子王', '辩护人', '搏击俱乐部', '饮食男女', '美丽心灵', '本杰明·巴顿奇事', '穿条纹睡衣的男孩',
                '窃听风暴', '情书', '两杆大烟枪', '西西里的美丽传说', '音乐之声', '看不见的客人', '拯救大兵瑞恩',
                '飞越疯人院', '小鞋子', '阿凡达', '哈利·波特与死亡圣器(下)', '沉默的羔羊', '致命魔术', '禁闭岛',
                '布达佩斯大饭店', '海豚湾', '蝴蝶效应', '美国往事', '心灵捕手', '低俗小说', '春光乍泄', '摩登时代',
                '功夫', '喜剧之王', '七宗罪', '哈利·波特与阿兹卡班的囚徒', '超脱', '致命ID', '杀人回忆', '红辣椒',
                '加勒比海盗', '狩猎', '被嫌弃的松子的一生', '7号房的礼物', '请以你的名字呼唤我', '哈利·波特与密室',
                '唐伯虎点秋香', '剪刀手爱德华', '一一', '断背山', '勇敢的心', '入殓师', '第六感', '爱在黎明破晓前',
                '重庆森林', '蝙蝠侠：黑暗骑士崛起', '幽灵公主', '天使爱美丽', '菊次郎的夏天', '小森林 夏秋篇',
                '阳光灿烂的日子', '超能陆战队', '爱在日落黄昏时', '完美的世界', '无人知晓', '消失的爱人', '甜蜜蜜',
                '借东西的小人阿莉埃蒂', '倩女幽魂', '小森林 冬春篇', '侧耳倾听', '时空恋旅人', '幸福终点站', '驯龙高手',
                '萤火之森', '寄生虫', '教父3', '怪兽电力公司', '一个叫欧维的男人决定去死', '玛丽和马克思', '未麻的部屋',
                '玩具总动员3', '傲慢与偏见', '神偷奶爸', '釜山行', '大鱼', '告白', '被解救的姜戈', '哈利·波特与火焰杯',
                '阳光姐妹淘', '射雕英雄传之东成西就', '新世界', '哪吒闹海', '我是山姆', '恐怖直播', '头号玩家',
                '模仿游戏', '血战钢锯岭', '喜宴', '七武士', '花样年华', '头脑特工队', '黑客帝国3：矩阵革命',
                '九品芝麻官', '电锯惊魂', '三块广告牌', '惊魂记', '你的名字。', '达拉斯买家俱乐部', '卢旺达饭店',
                '疯狂原始人', '上帝之城', '心迷宫', '谍影重重3', '英雄本色', '风之谷', '色，戒', '纵横四海', '海街日记',
                '茶馆', '岁月神偷', '记忆碎片', '爱在午夜降临前', '绿里奇迹', '忠犬八公物语', '荒蛮故事', '爆裂鼓手',
                '小偷家族', '疯狂的石头', '贫民窟的百万富翁', '无敌破坏王', '雨中曲', '东邪西毒', '冰川时代',
                '真爱至上', '恐怖游轮', '2001太空漫游', '你看起来好像很好吃', '黑天鹅', '无间道2', '魔女宅急便',
                '牯岭街少年杀人事件', '背靠背，脸对脸', '遗愿清单', '小丑', '雨人', '大佛普拉斯', '可可西里',
                '恋恋笔记本', '城市之光', '东京教父', '源代码', '初恋这件小事', '萤火虫之墓', '虎口脱险', '人工智能',
                '海边的曼彻斯特', '心灵奇旅', '罗生门', '青蛇', '波西米亚狂想曲', '终结者2：审判日',
                '疯狂的麦克斯4：狂暴之路', '新龙门客栈', '奇迹男孩', '二十二', '无耻混蛋', '房间', '千钧一发', '血钻',
                '崖上的波妞', '彗星来的那一夜', '黑客帝国2：重装上阵', '步履不停', '魂断蓝桥', '战争之王', '爱乐之城',
                '末路狂花', '谍影重重2', '火星救援', '燃情岁月', '千年女优', '阿飞正传', '花束般的恋爱',
                '再次出发之纽约遇见你', '谍影重重', '朗读者', '海洋', '香水', '穿越时空的少女', '地球上的星星',
                '我爱你', '哈利·波特与死亡圣器(上)', '弱点', '完美陌生人'}
tags = {
    "Action": "动作",
    "Adventure": "冒险",
    "Animation": "动画",
    "Anime": "动画",
    "Mini-Series": "短剧",
    "War & Politics": "政治",
    "Sci-Fi & Fantasy": "科幻",
    "Suspense": "悬疑",
    "Reality": "记录",
    "Comedy": "喜剧",
    "Crime": "犯罪",
    "Documentary": "纪录",
    "Drama": "剧情",
    "Family": "家庭",
    "Fantasy": "奇幻",
    "History": "历史",
    "Horror": "恐怖",
    "Music": "音乐",
    "Mystery": "悬疑",
    "Romance": "爱情",
    "Science Fiction": "科幻",
    "Sport": "体育",
    "Thriller": "惊悚",
    "War": "战争",
    "Western": "西部",
    "Biography": "传记",
    "Film-noir": "黑色",
    "Musical": "音乐",
    "Sci-Fi": "科幻",
    "Tv Movie": "电视",
    "Disaster": "灾难",
    "Children": "儿童",
    "Martial Arts": "武术",
    "Talk": "访谈",
    "Short": "短剧",
    "Game Show": "游戏",
    "Food": "美食",
    "Home and Garden": "家居园艺",
    "Travel": "旅行",
    "News": "新闻",
    "Soap": "肥皂剧",
    "Talk Show": "脱口秀",
    "Film-Noir": "黑色",
    "Indie": "独立",
    "IMDBtop250": "",
    "IMDBTop250": "",
    "DouBanTop250": "",
}


class plexsortout:
    def uniqify(self, seq):
        keys = {}
        for e in seq:
            keys[e] = 1
        return keys.keys()

    def check_contain_chinese(self, check_str):  # Judge chinese
        for ch in check_str:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    def chinese2pinyin(self, chinesestr):  # chinese to pyinyin
        pyinyin_list = []
        pinyin = pypinyin.pinyin(chinesestr, style=pypinyin.FIRST_LETTER, heteronym=True)
        for i in range(len(pinyin)):
            pyinyin_list.append(str(pinyin[i][0]).upper())
        pyinyin_str = ''.join(pyinyin_list)
        return pyinyin_str

    def removePunctuation(self, query):
        # 去除标点符号（只留字母、数字、中文)
        if query:
            rule = re.compile(u"[^a-zA-Z0-9]")
            query = rule.sub('', query)
        return query

    def updategenre(self, video, genres):
        englist = []
        chlist = []
        for tag in genres:
            enggenre = tag.tag
            if enggenre in tags.keys():
                englist.append(enggenre)
                zhQuery = tags[enggenre]
                chlist.append(zhQuery)
        if len(englist) > 0:
            video.addGenre(chlist, locked=False)
            video.removeGenre(englist, locked=True)
        else:
            video.addGenre(chlist, locked=True)

    def singleVideo(self, video):
        title = video.title
        # video.editTags(tag="actor", items=[x.tag for x in video.actors], remove=True)
        if video.titleSort:  # 判断是否已经有标题
            con = video.titleSort
            if (self.check_contain_chinese(con) or RECOVER):
                SortTitle = self.chinese2pinyin(title)
                SortTitle = self.removePunctuation(SortTitle)
                try:
                    video.editSortTitle(SortTitle)
                except Exception as e:
                    print(e)
                    print("Edit SortTitle error")
            for name in IMDBTop250:
                hastag = 0
                if name == title:
                    for tag in video.genres:
                        if tag.tag == "IMDB TOP 250":
                            hastag = 1
                            # rmlist=[]
                            # rmlist.append("Top250")
                            # print('remove Top250')
                            # video.removeGenre(rmlist, locked=True)

                    if hastag:
                        break
                    chlist = []
                    chlist.append("IMDB TOP 250")
                    video.addGenre(chlist, locked=True)

            for name in DouBanTop250:
                hastag = 0
                if name == title:
                    for tag in video.genres:
                        if tag.tag == "豆瓣 TOP 250":
                            hastag = 1
                    if hastag:
                        break
                    chlist = []
                    chlist.append("豆瓣 TOP 250")
                    video.addGenre(chlist, locked=True)

        if video.genres:
            video.reload()
            genres = video.genres
            self.updategenre(video, genres)

    def loopThroughAllMovies(self, videos):
        print("正在进行索引请稍候...")
        video_len = len(videos.all())
        for video, i in zip(videos.all(), range(video_len)):
            video.reload()
            j = int(i / video_len * 100)
            if i == video_len - 1:
                j = 100
            if ENABLE_LOG:
                print("\r", end="")
                print("进度: {}%: ".format(j), "█" * (j // 2), " " * (50 - j // 2),
                      end=str(i + 1) + "/" + str(video_len))
                sys.stdout.flush()
            title = video.title
            if video.titleSort:  # 判断是否已经有标题
                con = video.titleSort
                if (self.check_contain_chinese(con) or RECOVER):
                    SortTitle = self.chinese2pinyin(title)
                    SortTitle = self.removePunctuation(SortTitle)
                    try:
                        video.editSortTitle(SortTitle)
                    except Exception as e:
                        print(e)
                        print("Edit SortTitle error")
                #     continue
                # continue

            for name in IMDBTop250:
                hastag = 0
                if name == title:
                    for tag in video.genres:
                        if tag.tag == "IMDB TOP 250":
                            hastag = 1
                            # rmlist=[]
                            # rmlist.append("Top250")
                            # print('remove Top250')
                            # video.removeGenre(rmlist, locked=True)

                    if hastag:
                        break
                    chlist = []
                    chlist.append("IMDB TOP 250")
                    video.addGenre(chlist, locked=True)

            for name in DouBanTop250:
                hastag = 0
                if name == title:
                    for tag in video.genres:
                        if tag.tag == "豆瓣TOP 250":
                            hastag = 1
                    if hastag:
                        break
                    chlist = []
                    chlist.append("豆瓣TOP 250")
                    video.addGenre(chlist, locked=True)

            if video.genres:
                video.reload()
                genres = video.genres
                self.updategenre(video, genres)

    def process_all(self):
        # if os.path.isfile('./firstboot'):
        #     pass
        # else:
        _LOGGER.info("First Boot All libs Start!")
        servertype = MediaServerInstance.server_type
        if servertype == "plex":
            plex = MediaServerInstance.plex
            libtable = []
            for section in plex.library.sections():
                # if section.type == 'show' or section.type =='movie':
                print(section.title, section.key)
                # print(section.collections.title)
                libtable.append(section.title)

            for i in range(len(libtable)):
                print("\nStart NO." + str(i) + " " + libtable[i])
                videos = plex.library.section(libtable[i])
                self.loopThroughAllMovies(videos)
            _LOGGER.info("\n排序成功!")
        else:
            _LOGGER.error('仅支持配置了Plex媒体库的用户使用')

    def process(self):

        servertype = MediaServerInstance.server_type
        if servertype == "plex":
            plex = MediaServerInstance.plex
            libtable = []
            for section in plex.library.sections():
                # if section.type == 'show' or section.type =='movie':
                print(section.title, section.key)
                # print(section.collections.title)
                libtable.append(section.title)

            videos = plex.library.recentlyAdded()
            print("开始处理近10个添加的媒体 ")
            videoNum = 0
            for video in videos:
                videoNum = videoNum + 1
                if videoNum > 10:
                    break
                if video.type == "season":
                    parentkey = video.parentRatingKey
                    tvshows = plex.library.search(id=parentkey)
                    # plex.library.
                    print(tvshows[0].title)
                    self.singleVideo(tvshows[0])
                else:
                    print(video.title)
                    self.singleVideo(video)

            _LOGGER.info(f'[Plex Sort Out] Success!')
        else:
            _LOGGER.info(f'[Plex Sort Out] [None Plex Server] Fail!')

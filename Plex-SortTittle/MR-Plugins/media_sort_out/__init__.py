"""
随便把想要插件初始化的类定义为什么文件名，只要在__init__导入就可以
也可以把命令和事件直接写在__init__文件里，没有限制
"""
from .event import *
from .command import *
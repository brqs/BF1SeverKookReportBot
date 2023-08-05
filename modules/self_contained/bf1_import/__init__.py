from core.bot import bot
from loguru import logger
import time
import socket
import json
import time
import threading
import random
from queue import Queue
from zhconv import convert  
from .utils import get_server_all_report,get_server_report_random
from .utils import get_gid,get_mapname,get_server_status
from utils.bf1.database import BF1DB
from utils.bf1.default_account import BF1DA
from khl import PublicMessage, MessageTypes
from collections import Counter
import zhconv
import difflib
# 游戏聊天服务器地址和端口
GAME_CHAT_ADDRESS = '127.0.0.1'
GAME_CHAT_PORT = 51001
# 我们应用程序的地址和端口
APP_ADDRESS = '127.0.0.1'
APP_PORT = 51002
# 发送消息的频率限制（秒）
SEND_FREQ_LIMIT = 1
#发送聊天消息的频道
SEND_MESSAGE_CL=None
SEND_MESSAGE_CLID='6514532698005389'
REPORT_MESSAGE_CL=None
REPORT_MESSAGE_CLID='6491099642265366'
# 初始化 UDP socket 用于接收游戏聊天消息
recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_socket.bind((APP_ADDRESS, APP_PORT))
# 初始化 UDP socket 用于发送游戏聊天消息
send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 初始化变量以跟踪发送频率
last_send_time = 0
lock = threading.Lock()
# 初始化 zhconv 转换器，用于繁简中文转换
converter = convert

# 创建队列用于存储待发送的消息
message_queue = Queue()

#初始化聊天信息存储容器
message_set={'存储聊天信息的集合'}
sended_message_set={'存储聊天信息的集合'}
#初始化投票容器
VOTE_DICT={}
def receive_chat():
    """
    用于在后台接收游戏聊天消息的函数。
    在单独的线程中运行。
    """
    global VOTE_DICT
    while True:
        data, addr = recv_socket.recvfrom(1024)
        message = data.decode('utf-8')
        if message.startswith('{'):
            message_data = json.loads(message)
            send_message=f"`{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))}`服务器ddf1玩家`{message_data['name']}`说{message_data['content']}\n"
            message_set.add(send_message)
            if message_data['content'].isdigit():
                if 1<=int(message_data['content'])<=5:
                    VOTE_DICT[message_data['name']]=message_data['content']
                 
def send_chat_worker():
    """
    用于从队列中取出消息并发送到游戏聊天服务器的函数。
    在单独的线程中运行。
    """
    while True:
        message = message_queue.get()
        # 将消息转换为繁体中文
        if type(message) ==str:
            text = converter(message, 'zh-tw')
            # 将消息编码为 UTF-8 字节
            time1=time.time()
            message = f"#Chat.Send#{text}".encode('utf-8')
            try:
                logger.info(f'发送{text}中')
                send_socket.sendto(message, (GAME_CHAT_ADDRESS, GAME_CHAT_PORT))
                time.sleep(1)
                # 发送完毕后移除消息
            except Exception as e:
                print(f"发送游戏聊天消息时出错：{e}")
            finally:
                message_queue.task_done()
                time2=time.time()
                logger.info(f'发送完成，剩余消息队列长度为{message_queue.qsize()}，耗时{time2-time1}')
# 启动线程以发送消息
send_thread = threading.Thread(target=send_chat_worker)
send_thread.daemon = True
send_thread.start()
# 启动线程以接收游戏聊天消息
receive_thread = threading.Thread(target=receive_chat)
receive_thread.daemon = True
receive_thread.start()

@bot.task.add_interval(seconds=60)
async def send_server_report():
    """
    将服务器报告添加到待发送消息队列中。
    """
    try:
        str1=get_server_report_random()
        message_queue.put(str1)
    except Exception as e:
        logger.exception(e)
def sort_by_time(message):
    time_str = message.split('`')[1]  # 解析出时间字符串
    timestamp = time.mktime(time.strptime(time_str, '%Y/%m/%d %H:%M:%S'))  # 转换为时间戳
    return timestamp
@bot.task.add_interval(seconds=6)
async def send_receive_chat():
    global message_set,sended_message_set,SEND_MESSAGE_CL,SEND_MESSAGE_CLID
    if message_set==sended_message_set:
        return False
    send_message_set=message_set-sended_message_set
    for e in message_set:
        sended_message_set.add(e)
    sorted_messages = sorted(send_message_set, key=sort_by_time)
    send_message="".join(s for s in sorted_messages)
    if SEND_MESSAGE_CL is None:
        SEND_MESSAGE_CL=await bot.client.fetch_public_channel(SEND_MESSAGE_CLID)
    await bot.client.send(target=SEND_MESSAGE_CL, content=send_message)
cl2=None
@bot.task.add_interval(seconds=300)
async def send_message_servers():
    global cl2
    if cl2 is None:
        cl2=await bot.client.fetch_public_channel('6491099642265366')
    send_str=get_server_all_report()
    await bot.client.send(target=cl2, content=send_str)  
 
# @bot.command(name="say", aliases=["s"], prefixes=["-"])   
# async def say(msg: PublicMessage, content: str = None):
#     message_queue.put(content)
##投票换图
async def get_map_list_rand5():
    server_gid = get_gid()
    # 获取地图池
    result = await (await BF1DA.get_api_instance()).getServerDetails(server_gid)
    if type(result) == str:
        return f"获取图池时网络出错!"
    map_list = []
    choices = []
    i = 0
    result = result['result']
    for item in result["rotation"]:
        map_list.append(
            f"{item['modePrettyName']}-{item['mapPrettyName']}●\n".replace('流血', '流\u200b血')
            if (
                    item['modePrettyName'] == '行動模式'
                    and
                    item['mapPrettyName'] in
                    [
                        '聖康坦的傷痕', '窩瓦河',
                        '海麗絲岬', '法歐堡', '攻佔托爾', '格拉巴山',
                        '凡爾登高地', '加利西亞', '蘇瓦松', '流血宴廳', '澤布呂赫',
                        '索姆河', '武普庫夫山口', '龐然闇影'
                    ]
            )
            else f"{item['modePrettyName']}-{item['mapPrettyName']}".replace('流血', '流\u200b血')
        )
        choices.append(str(i))
        i += 1
    map_list_rand5 = random.sample(map_list, 5)
    return map_list_rand5
#定时发送投票消息
randmap=[]
@bot.task.add_interval(seconds=65)
async def test():
    global randmap
    if randmap==[]:
        randmap=await get_map_list_rand5()
    map_list_str=' '.join(f'{i+1}.{v.split("-")[1][:3]}({v.split("-")[0][:1]})' for i, v in enumerate(randmap))
    vote_strat=f"dsz vote:投票换图,下局图池{map_list_str}"
    vote_rule=f"dsz vote:投票规则,当局结束前在公屏发送纯数字即可,每人一票,本局游戏结束后切换"
    if get_server_status()=="going":
        message_queue.put(vote_strat)
        time.sleep(2)
        message_queue.put(vote_rule)
#定时发送投票情况
@bot.task.add_interval(seconds=180)
async def test1():
    global VOTE_DICT
    if VOTE_DICT !={}:
        value_counts = Counter(VOTE_DICT.values())
        max_count = max(value_counts.values())
        max_count_values = [value for value, count in value_counts.items() if count == max_count][0]
        vote_info=f"dsz vote:当前得分最高是地图{max_count_values}票数{max_count},至少超过三票才会被切换"
        if get_server_status()=="going":
            message_queue.put(vote_info)

@bot.task.add_interval(seconds=1)
async def Listen_stauts():
    global VOTE_DICT,randmap
    if VOTE_DICT =={}:
        return False
    if get_server_status()=="end" or get_server_status() is None:
        value_counts = Counter(VOTE_DICT.values())
        max_count = max(value_counts.values())
        max_count_values = [value for value, count in value_counts.items() if count == max_count][0]
        logger.info(f"是否切图{max_count >=1}")
        if max_count >=1:
            server_gid=get_gid()
            result = await (await BF1DA.get_api_instance()).getServerDetails(server_gid)
            guid = result['result']['guid']
            map_index = randmap[int(max_count_values)-1] 
            # 1.地图池
            i = 0
            map_list=[]
            result = result['result']
            for item in result["rotation"]:
                map_list.append(f"{item['modePrettyName']}-{item['mapPrettyName']}")
                i += 1
            if map_index != "重開":
                map_index_list = []
                for map_temp in map_list:
                    if map_index in map_temp:
                        if map_temp not in map_index_list:
                            map_index_list.append(map_temp)
                if len(map_index_list) == 0:
                    map_index_list = list(set(difflib.get_close_matches(map_index, map_list)))
            if len(map_index_list) == 1:
                if type(map_index_list[0]) != int:
                    map_index = map_list.index(map_index_list[0])
                else:
                    map_index = map_index_list[0]
            result=await (await BF1DA.get_api_instance()).chooseLevel(guid,map_index)
            if type(result)==dict:
                await bot.client.send(target=SEND_MESSAGE_CL, content=f"`{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))}`服务器地图通过投票更换为{map_index_list[0]}")
        VOTE_DICT={}
        randmap=[]

# @bot.task.add_interval(seconds=1)
# async def test():
#     mplist=await get_map_list()
#     logger.info(mplist)
    



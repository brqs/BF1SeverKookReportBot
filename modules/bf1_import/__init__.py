from core.bot import bot
from loguru import logger
import time
import yaml
from collections import Counter
import random
import difflib
from utils.bf1.client_utils import  Clientutils
from utils.bf1.database import BF1DB
from utils.bf1.default_account import BF1DA
from utils.bf1.client_sr import gc 
from utils.bf1.client_records import gk
from khl import PublicMessage
#从配置文件读取
with open('./config/config.yaml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)
    SEND_MESSAGE_CL=None
    SEND_MESSAGE_CLID= data['botinfo'].get('chat_channel')[0]
    REPORT_MESSAGE_CL=None
    REPORT_MESSAGE_CLID=data['botinfo'].get('report_channel')[0]
    BANWEAPON_MESSAGE_CL=None
    BANWEAPON_MESSAGE_CLID=data['botinfo'].get('autokick_channel')[0]
    REPORTTIME=data['botinfo'].get('report_time')[0]
    PLAYLIST_MESSAGE_CL=None
    PLAYLIST_MESSAGE_CLID=data['botinfo'].get('playerlist_channel')[0]
    send_kick_list=[]
    KICK_DICT={}
    VOTE_NUM=data['botinfo'].get('vote_num')[0]
#聊天信息的定时转发，已过滤机器人消息
@bot.task.add_interval(seconds=6)
async def send_receive_chat():
    global SEND_MESSAGE_CL,SEND_MESSAGE_CLID
    if SEND_MESSAGE_CL is None:
        SEND_MESSAGE_CL=await bot.client.fetch_public_channel(SEND_MESSAGE_CLID)
    message=gc.get_send_kook_message()
    if message != "" and message != False:
        await bot.client.send(target=SEND_MESSAGE_CL, content=message)
#简报输出频道
@bot.task.add_interval(seconds=300)
async def send_message_servers():
    global REPORT_MESSAGE_CL,REPORT_MESSAGE_CLID
    if REPORT_MESSAGE_CL is None:
        REPORT_MESSAGE_CL=await bot.client.fetch_public_channel(REPORT_MESSAGE_CLID)   
    send_report=Clientutils.get_server_report("all")
    if send_report!=False :
        await bot.client.send(target=REPORT_MESSAGE_CL, content=send_report) 
#随机输出报告
@bot.task.add_interval(seconds=REPORTTIME)
async def send_server_report():
    try:
        str1=Clientutils.get_server_report_random()
        gc.message_queue.put(str1)
    except Exception as e:
        logger.exception(e)
#添加禁武器
@bot.command(name="add_ban_wepaon",aliases=['banwepaon','bw'],prefixes=['-'])
async def add_ban_wepaon(msg: PublicMessage,weapon:str,banname:str="default"):
    banlist=[weapon]
    if (await BF1DB.update_weapon_ban(banname,banlist))!=False:
        await msg.reply(f"添加禁用{weapon}成功")
    else:
        await msg.reply(f"添加禁用{weapon}失败")
@bot.command(name="list_ban_wepaon",aliases=['listbanwepaon','lbw'],prefixes=['-'])
async def list_ban_wepaon(msg: PublicMessage,banname:str="default"):
    banlist=await BF1DB.get_weapon_ban(banname)
    await msg.reply("禁用武器列表如下："+"\n".join(i for i in banlist))
@bot.command(name="del_ban_wepaon",aliases=['delbanwepaon','dbw'],prefixes=['-'])
async def list_ban_wepaon(msg: PublicMessage,weapon:str,banname:str="default"):
    if (await BF1DB.del_weapon_ban(banname,weapon))!=False:
        await msg.reply(f"删除禁用{weapon}成功")
    else:
        await msg.reply(f"删除禁用{weapon}失败")   
#自动踢出禁用
@bot.task.add_interval(seconds=2)
async def check():
    #添加踢出字典
    global KICK_DICT
    banlist=await BF1DB.get_weapon_ban("default")
    result_name=Clientutils.get_server_who_use_ban_weapon(banlist)
    for v in result_name:
        KICK_DICT[list(v.keys())[0]]=list(v.values())[0]
@bot.task.add_interval(seconds=1)
async def auto_kick():
    global KICK_DICT,send_kick_list,BANWEAPON_MESSAGE_CL,BANWEAPON_MESSAGE_CLID
    if KICK_DICT =={}:
        return False
    server_gid = Clientutils.get_gid()
    if server_gid is None: return False
    for k,v in KICK_DICT.items():
        time_now = time.strftime('%Y/%m/%d/%H:%M:%S', time.localtime(time.time()))
        send_str=f"`{time_now}`玩家`{k}`使用违规武器 `{v[1]}`" 
        reason=f"ban{v[1]}"
        result = await (await BF1DA.get_api_instance()).kickPlayer(server_gid, v[0], 'kick:Use of illegal weapons')
        logger.info(result)
        if type(result) == str:
            send_str+=" "+result+'\n'
            return False
        elif type(result) == dict:
            send_str+=" "+"已踢出"+'\n'
        if send_str not in send_kick_list:
            send_kick_list.append(send_str)
            gc.message_queue.put(f"dsz autokick:{k}使用违规武器 {v[1]}已踢出")
    if send_kick_list!=[]:
        if BANWEAPON_MESSAGE_CL is None:
            BANWEAPON_MESSAGE_CL=await bot.client.fetch_public_channel(BANWEAPON_MESSAGE_CLID)
        text="\n".join(i for i in send_kick_list)
        await bot.client.send(target=BANWEAPON_MESSAGE_CL, content=text)
    send_kick_list=[]
    KICK_DICT={}
#玩家列表变动相关
@bot.task.add_interval(seconds=30)
async def check_playerlist():
    new,left,swap=Clientutils.player_list_changes_report("all")
    send=""
    if new !=False: send+=new+"\n"
    if left !=False: send+=left+"\n"
    if swap !=False: send+=swap
    Clientutils.player_list_changes_report("update")
    global PLAYLIST_MESSAGE_CL,PLAYLIST_MESSAGE_CLID
    if PLAYLIST_MESSAGE_CL is None:
        PLAYLIST_MESSAGE_CL=await bot.client.fetch_public_channel(PLAYLIST_MESSAGE_CLID)
    if send!="":     
        await bot.client.send(target=PLAYLIST_MESSAGE_CL, content=send) 
#击杀记录计入数据库
@bot.task.add_interval(seconds=30)
async def status():
    for i in range(gk.return_queue.qsize()):
        data=gk.return_queue.get()
        await BF1DB.add_record(data)
#投票换图

@bot.task.add_interval(seconds=0.5)
async def vote_map():
    global VOTE_NUM
    if gc.mapdict=={}:
        return False
    try:
        status=Clientutils.get_server_data("status")["stateName"]
    except Exception as e:
        status = "error"
    values = list(gc.mapdict.values())
    counter = Counter(values)
    most_common_value, count = counter.most_common(1)[0]
    if status=="Waiting For Level Loaded":
        if count>=VOTE_NUM:
            server_gid=Clientutils.get_gid()
            result = await (await BF1DA.get_api_instance()).getServerDetails(server_gid)
            guid = result['result']['guid']
            map_index = gc.map[int(most_common_value)-1] 
            i = 0
            map_list=[]
            result = result['result']
            for item in result["rotation"]:
                map_list.append(f"{item['modePrettyName']}-{item['mapPrettyName']}")
                i += 1
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
            message=f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}服务器地图通过投票更换为{map_index_list[0]}"
            gc.message_queue.put(message)
            message=f"`{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}`服务器地图通过投票更换为`{map_index_list[0]}`"
            await bot.client.send(target=SEND_MESSAGE_CL, content=message)
            gc.map=[]
            gc.mapdict={}
        else:
            gc.map=[]
            gc.mapdict={}
    else:
        return False
async def get_map_list_rand5():
    server_gid = Clientutils.get_gid()
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
@bot.task.add_interval(seconds=30)
async def vote_map_info():
    if gc.map==[]:
        gc.map=await get_map_list_rand5()
        logger.info(f"初始化随机切换地图池{gc.map}")
    map_list_str=' '.join(f'{i+1}.{v.split("-")[1][:4]}({v.split("-")[0][:2]})' for i, v in enumerate(gc.map))
    vote_strat=f"dsz vote:投票换图,下局图池{map_list_str}"
    gc.message_queue.put(vote_strat)
    if gc.mapdict!={}:
        values = list(gc.mapdict.values())
        counter = Counter(values)
        most_common_value, count = counter.most_common(1)[0]
        gc.message_queue.put(f"dsz vote:当前投票最多的地图是{gc.map[int(most_common_value)-1]}({count}),超过三票才会切换")
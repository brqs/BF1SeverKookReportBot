from core.bot import bot
from loguru import logger
import time
import yaml
from utils.bf1.client_utils import  Clientutils
from utils.bf1.database import BF1DB
from utils.bf1.default_account import BF1DA
from utils.bf1.client_sr import gc 
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
async def test1():
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
@bot.task.add_interval(seconds=0.25)
async def status():
    logger.info(f"status:{Clientutils.get_server_data('status')['stateName']},InGame:{Clientutils.get_server_data('status')['statusName']}, isChatManagerValid:{Clientutils.get_server_data('chat')['isChatManagerValid']},status:{Clientutils.get_server_status()}")
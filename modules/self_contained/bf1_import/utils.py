from loguru import logger
import requests
import time
import random
import statistics
gid_temp=[]
def get_gid():
    global gid_temp
    if len(gid_temp)>50:
        del gid_temp[0:45]
    try:
        data=get_server_info_data()
        gid_temp.append(data["gameId"])
        return data["gameId"]
    except Exception as e:
        if len(gid_temp)!=0:
            return gid_temp[-1]
def get_sname():
    data=get_server_info_data()
    return data["name"]
def get_mapname():
    data=get_server_info_data()
    return data["mapName2"]
def get_count(lst:list,key:str,value): 
    count = sum(1 for d in lst if d.get(key) == value)
    return  count
def get_playerlist(lst:list):
    result_lst = [{k: d[k] for k in ['name', 'rank', 'kill', 'death']} for d in lst if all(key in d for key in ['name', 'rank', 'kill', 'death'])]
    return result_lst   
def get_king(lst:list):
    max_kill = max([d.get('kill', 0) for d in lst])
    result = next(d.get('name', 'dsz') for d in lst if d.get('kill', 0) == max_kill)
    return max_kill, result
def get_hot(lst:list,key):
    hot_counts = {}
    for d in lst:
        if d[key] is  None:
            continue
        if d[key]['name'] != "" :
           hot_counts[d[key]['name']] = hot_counts.get(d[key]['name'], 0) + 1
    maxhot_count = max(hot_counts.values())
    result = next(d[key]['name'] for d in lst if d[key] is not None and d[key]['name'] == max(hot_counts, key=hot_counts.get))
    return result
server_status_temp=[]
def get_server_status():
    try:
        total_kill,total_death=get_server_total_kd()
        isEnd=False
    except Exception as e:
        isEnd=True
    global server_status_temp
    if len(server_status_temp)>50:
        del server_status_temp[0:40]
    if isEnd:
        if len(server_status_temp)!=0 and server_status_temp[-1]=="going":
            server_status_temp.append("end")
            return "end"
    else:
        server_status_temp.append("going")
        return "going"

def get_server_data():
    return get_server_data_total(),get_server_data_team(1),get_server_data_team(2)
def get_server_data_total():
    url='http://127.0.0.1:10086/Player/GetAllPlayerList'
    headers = {"Connection": "keep-alive"}
    timeout = 3
    response = requests.get(url, headers=headers, timeout=timeout)
    data=response.json()
    return data
def get_server_data_team(index: int):
    url = f'http://127.0.0.1:10086/Player/GetTeam{index}PlayerList'
    headers = {"Connection": "keep-alive"}
    timeout = 3
    response = requests.get(url, headers=headers, timeout=timeout)
    return response.json()
def get_server_info_data():
    url='http://127.0.0.1:10086/Server/GetServerData'
    headers = {"Connection": "keep-alive"}
    timeout = 3
    response = requests.get(url, headers=headers, timeout=timeout)
    return response.json()
def get_server_info():
    url='http://127.0.0.1:10086/Server/GetServerData'
    headers = {"Connection": "keep-alive"}
    timeout = 3
    response = requests.get(url, headers=headers, timeout=timeout)
    servername=response.json()['name'][:20]+'\n'
    mapmode=response.json()['gameMode2']+'-'+response.json()['mapName2']+'\n'
    team="队伍1:"+response.json()["team1"]['name']+"  队伍2:"+response.json()["team2"]['name']+'\n'
    server=servername+mapmode+team
    return server
def get_server_total_kd():
    total_data=get_server_data_total()
    total_kill= sum([d.get('kill', 0) for d in total_data])
    total_death=sum([d.get('dead', 0) for d in total_data])
    return total_kill, total_death
def get_server_kd():
    total_data,team1_data,team2_data=get_server_data()
    total_kill= sum([d.get('kill', 0) for d in total_data])
    total_death=sum([d.get('dead', 0) for d in total_data])
    team1_kill= sum([d.get('kill', 0) for d in team1_data])
    team1_death= sum([d.get('dead', 0) for d in team1_data])
    team2_kill= sum([d.get('kill', 0) for d in team2_data])
    team2_death= sum([d.get('dead', 0) for d in team2_data])
    return total_kill,total_death,team1_kill,team1_death,team2_kill,team2_death
def get_server_mean_rank():
    total_data,team1_data,team2_data=get_server_data()
    total_rank=sum([d.get('rank', 0) for d in total_data])/len(total_data)
    team1_rank= sum([d.get('rank', 0) for d in team1_data])/len(team1_data)
    team2_rank= sum([d.get('rank', 0) for d in team2_data])/len(team2_data)
    return int(total_rank),int(team1_rank), int(team2_rank)
def get_server_king():
    total_data,team1_data,team2_data=get_server_data()
    total_kill_max,total_kill_king=get_king(total_data)
    team1_kill_max,team1_kill_king=get_king(team1_data)
    team2_kill_max,team2_kill_king=get_king(team2_data)
    total_death_max = max([d.get('dead', 0) for d in total_data])
    total_death_king = next(d.get('name', 'dsz') for d in total_data if d.get('dead', 0) ==  total_death_max)
    return total_kill_max,total_kill_king,total_death_max,total_death_king,team1_kill_max,team1_kill_king,team2_kill_max,team2_kill_king

def get_server_hot():
    total_data=get_server_data_total()
    hot_weapon=get_hot(total_data,'weaponS0')  
    hot_grenade=get_hot(total_data,'weaponS6') 
    hot_knife=get_hot(total_data,'weaponS7') 
    return hot_weapon,hot_grenade,hot_knife
def get_server_num():
    total_data,team1_data,team2_data=get_server_data()
    return len(total_data),len(team1_data),len(team2_data)
def get_server_150():
    total_data,team1_data,team2_data=get_server_data()
    total_150=get_count(total_data,'rank',150)
    team1_150=get_count(team1_data,'rank',150)
    team2_150=get_count(team2_data,'rank',150)
    return total_150, team1_150, team2_150
def get_server_admin():
    total_data=get_server_data_total()
    true=True
    admin_num=get_count(total_data,'isAdmin',true)
    admin_names = [d['name'] for d in total_data if d.get('isAdmin') == True]
    return admin_num,admin_names
def get_server_vip():
    total_data=get_server_data_total()
    true=True
    vip_num=get_count(total_data,'isVip',true)
    return vip_num
def get_server_luck():
    total_data=get_server_data_total()
    luck=total_data[random.randint(0,len(total_data)-1)]['name']
    return luck
def get_server_playlist():
    total_data,team1_data,team2_data=get_server_data()
    total_list=get_playerlist(total_data)
    team1_list=get_playerlist(team1_data)
    team2_list=get_playerlist(team2_data)
    return total_list,team1_list,team2_list
def get_server_all_report():
    report="-"*20+'\n'
    server=get_server_info()
    total_kill,total_death,team1_kill,team1_death,team2_kill,team2_death=get_server_kd()
    total_rank,team1_rank,team2_rank=get_server_mean_rank()
    total_kill_max,total_kill_king,total_death_max,total_death_king,team1_kill_max,team1_kill_king,team2_kill_max,team2_kill_king=get_server_king()
    hot_weapon,hot_grenade,hot_knife=get_server_hot()
    total_num,team1_num,team2_num=get_server_num()
    admin_num,admin_names=get_server_admin()
    vip_num=get_server_vip()
    total_150, team1_150, team2_150=get_server_150()
    luck=get_server_luck()
    report+=server+'服务器服内简报:\n'+f"服务器服内简报:\n更新时间(`{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))}`)\n"\
        +f'共有玩家{total_num}名\n'+f'管理数({admin_num})  vip数({vip_num})  150数({total_150})'+f'服内平均等级{total_rank}\n'+f'总击杀数为{total_kill}  总死亡数为{total_death}\n'\
        +f'击杀王为`{total_kill_king}`({total_kill_max})  狗带王为`{total_death_king}`({total_death_max})\n'\
        +f'幸运玩家为`{luck}`\n'+f'热门主武器为{hot_weapon}\n'+f'热门近战武器为{hot_knife}\n'+f'热门投掷武器为{hot_grenade}\n'\
        +f'-'*20+'\n队伍1信息:\n'+f"人数{team1_num}  总击杀数{team1_kill}  总死亡数{team1_death}\n"\
        +f'平均等级{team1_rank}  150玩家数为{team1_150}\n'+f"1队击杀王为`{team1_kill_king}`({team1_kill_max})\n"\
        +f'-'*20+'\n队伍2信息:\n'+f"人数{team2_num}  总击杀数{team2_kill}  总死亡数{team2_death}\n"\
        +f'平均等级{team2_rank}  150玩家数为{team2_150}\n'+f"1队击杀王为`{team2_kill_king}`({team2_kill_max})\n"\
        +'\n\n'
    return report
def get_server_kd_report():
    total_kill,total_death,team1_kill,team1_death,team2_kill,team2_death=get_server_kd()
    report=f"dsz report:总kill数为{total_kill},总dead数为{total_death},t1kill数为{team1_kill}，t1dead为{team2_death},t2kill数为{team2_kill}，t2dead数为{team2_death}"
    return report
def get_server_rank_report():
    total_rank,team1_rank,team2_rank=get_server_mean_rank()
    report=f"dsz report:平均等级为{total_rank},team1平均等级为{team1_rank},team2平均等级为{team2_rank}"
    return report
def get_server_kill_total_report():
    total_kill_max,total_kill_king,total_death_max,total_death_king,team1_kill_max,team1_kill_king,team2_kill_max,team2_kill_king=get_server_king()
    report=f"dsz report:击杀王{total_kill_king}({total_kill_max}),狗带王{total_death_king}({total_death_max})"
    return report
def get_server_kill_team_report():
    total_kill_max,total_kill_king,total_death_max,total_death_king,team1_kill_max,team1_kill_king,team2_kill_max,team2_kill_king=get_server_king()
    report=f"dsz report:1队击杀王{team1_kill_king}({team1_kill_max}),2队击杀王{team2_kill_king}({team2_kill_max})"
    return report
def get_server_luck_report():
    luck=get_server_luck()
    report=f"dsz report:{luck}被选为幸运玩家"
    return report
def get_server_admin_report():
    admin_num,admin_names=get_server_admin()
    if admin_num==0:
        report=f"dsz report:当前无服务器管理在线,发现违规行为请加入kook反馈"
    else:
        admin_name="".join(i+" " for i in admin_names)
        report=f"dsz report:当前{admin_num}位管理在线,admin id:{admin_name}"
    return report
def get_server_hot_weapon_report():
    hot_weapon,hot_grenade,hot_knife=get_server_hot()
    report=f"dsz report:你知道吗?当前使用最多的主武器是{hot_weapon}"
    return report
def get_server_hot_grenade_report():
    hot_weapon,hot_grenade,hot_knife=get_server_hot()
    report=f"dsz report:你知道吗?当前使用最多的投掷物是{hot_grenade}"
    return report        
def get_server_hot_knife_report():
    hot_weapon,hot_grenade,hot_knife=get_server_hot()
    report=f"dsz report:你知道吗?当前使用最多的刀是{hot_knife}"
    return report
def get_server_150_report():
    total_150, team1_150, team2_150=get_server_150()                 
    report=f"dsz report:当前服务器150级玩家有{total_150}位,队伍1有{team1_150}位,队伍2有{team2_150}位"
    return report 
def get_server_tips():
    tips = [
    "dsz tips:服务器禁用炸药,1903exp,空爆迫击炮,闪光",
    "dsz tips:定点武器机枪是可以使用的,毕竟那是灵位,对吧",
    "dsz tips:at筒子可以使用,单发能瞄准,就是栓",
    "dsz tips:如果你想的话aa筒平射也可以",
    "dsz tips:总所周知两个支援兵可以相互补给发射器",
    "dsz tips:midway是一种十分有趣的生物",
    "dsz tips:毒气绊雷和周遭警戒更配",
    "dsz tips:大栓服毒气绊雷玩法开创者是midway",
    "dsz tips:你知道ddf 1111古神吗?",
    "dsz tips:大栓服为什么没有手枪这是一个说来话长的故事",
    "dsz tips:早期大栓服是抢攻为主的，但现在是以团队死斗为主",
    "dsz tips:或许你应该知道三炮打散ddf的故事",
    "dsz tips:dsz是什么意思，其实很简单就是dashuanzi(迫真",
    "dsz tips:ddf又是什么呢?黑暗地牢(x),打东风(yes)麻将馆",
    "dsz tips:如果你有什么好的建议请加入kook或qq与its联系",
    "dsz tips:参与暖服可以自助恰v",
    "dsz tips:多数时候,你看到我出现时,已开启1903exp kill"
]
    return tips[random.randint(0, len(tips)-1)]
def get_server_rules():
    rules = [
    "dsz rules:服务器禁用炸药,1903exp,空爆迫击炮,闪光,其他武器无限制",
    "dsz rules:如果你对该机器人功能感兴趣请加入ddf kook服务器:https://kook.top/A17StS",
    "dsz rules:出现外挂,请加入qq群或者kook向管理员反馈",
    "dsz rules:150请自觉平衡不要抱团捞薯",
    "dsz rules:如果你希望加入ddf管理团队请加入qq群和kook"
]
def get_server_join():
    rules = [
    "dsz invite:ddf服务器QQ群号838082738,ddf kook服务器:https://kook.top/A17StS",
    "dsz invite:如果你对该机器人功能感兴趣请加入ddf kook服务器:https://kook.top/A17StS",
]
    return rules[random.randint(0, len(rules)-1)]            
def get_server_report_random():
    try:
        # 定义每个函数的权重
        report_funcs = [
            (get_server_kd_report, 2),
            (get_server_rank_report, 2),
            (get_server_kill_total_report, 2),
            (get_server_kill_team_report, 1),
            (get_server_luck_report, 1),
            (get_server_admin_report, 2),
            (get_server_hot_weapon_report, 1),
            (get_server_hot_knife_report, 1),
            (get_server_150_report, 1),
            (get_server_tips,2),
            (get_server_rules,2),
            (get_server_join,2)
        ]
        choices = []
        weights = []
        for func, weight in report_funcs:
                result = func()
                choices.append(result)
                weights.append(weight)
        result=random.choices(choices, weights=weights)[0]
    except Exception as e:
        report_funcs = [
                       (get_server_tips,2),
                        (get_server_rules,2),
                        (get_server_join,2)
                    ]
        choices = []
        weights = []
        for func, weight in report_funcs:
                result = func()
                choices.append(result)
                weights.append(weight)
        result=random.choices(choices, weights=weights)[0]
    return result           
def get_server_who_use_ban_weapon(banlist:list):
    total_data=get_server_data_total()
    result_names = []
    for data in total_data:
        for i in range(8):
            weapon_key = "weaponS" + str(i)
            if weapon_key in data and data[weapon_key]!=None and data[weapon_key]["name"] in banlist:
                result_names.append({data["name"]:[data["personaId"],data[weapon_key]["name"]]})
    return result_names
            
print(get_server_who_use_ban_weapon(["炸药", "特殊载具 空爆迫击炮", "M1903（实验）", "信号枪（闪光）"]))
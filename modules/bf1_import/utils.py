from loguru import logger
import requests
import time
import random
import statistics

gid_temp = []


def get_gid():
    """
    获取游戏ID。

    Returns:
        str: 游戏ID。
    """
    global gid_temp

    # 如果gid_temp超过50个元素，则删除前45个元素
    if len(gid_temp) > 50:
        del gid_temp[0:45]

    try:
        data = get_server_info_data()
        gid_temp.append(data["gameId"])
        return data["gameId"]
    except Exception as e:
        # 如果gid_temp不为空，则返回最后一个元素
        if len(gid_temp) != 0:
            return gid_temp[-1]


def get_sname():
    """
    获取服务器名称。

    Returns:
        str: 服务器名称。
    """
    data = get_server_info_data()
    return data["name"]


def get_mapname():
    """
    获取地图名称。

    Returns:
        str: 地图名称。
    """
    data = get_server_info_data()
    return data["mapName2"]


def get_count(lst: list, key: str, value):
    """
    计算列表中特定键值对出现的次数。

    Args:
        lst (list): 包含字典元素的列表。
        key (str): 键名。
        value: 键值。

    Returns:
        int: 键值对出现的次数。
    """
    count = sum(1 for d in lst if d.get(key) == value)
    return count


def get_playerlist(lst: list):
    """
    获取玩家列表。

    Args:
        lst (list): 包含字典元素的列表。

    Returns:
        list: 包含玩家字典的列表。
    """
    result_lst = [
        {k: d[k] for k in ['name', 'rank', 'kill', 'death']}
        for d in lst
        if all(key in d for key in ['name', 'rank', 'kill', 'death'])
    ]
    return result_lst


def get_king(lst: list):
    """
    获取击杀王信息。

    Args:
        lst (list): 包含字典元素的列表。

    Returns:
        Tuple[int, str]: 最大击杀数和击杀王的名称。
    """
    max_kill = max([d.get('kill', 0) for d in lst])
    result = next(d.get('name', 'dsz') for d in lst if d.get('kill', 0) == max_kill)
    return max_kill, result


def get_hot(lst: list, key):
    """
    获取热门信息。

    Args:
        lst (list): 包含字典元素的列表。
        key: 键名。

    Returns:
        str: 热门信息。
    """
    hot_counts = {}
    for d in lst:
        if d[key] is None:
            continue
        if d[key]['name'] != "":
            hot_counts[d[key]['name']] = hot_counts.get(d[key]['name'], 0) + 1
    maxhot_count = max(hot_counts.values())
    result = next(
        d[key]['name']
        for d in lst
        if d[key] is not None and d[key]['name'] == max(hot_counts, key=hot_counts.get)
    )
    return result


server_status_temp = []
ISINSERVER = False


def get_server_status():
    """
    获取服务器状态。

    Returns:
        str: 服务器状态，可能的取值为 "going" 或 "end"。
    """
    try:
        global ISINSERVER, server_status_temp
        url = 'http://127.0.0.1:10086/Game/GetGameStatus'
        headers = {"Connection": "keep-alive"}
        timeout = 3
        response = requests.get(url, headers=headers, timeout=timeout)
        data = response.json()['data']
        if data['statusName'] == "Ingame":
            ISINSERVER = True
        else:
            ISINSERVER = False
            logger.warning("bot not in server")
            return "noserver"
        if len(server_status_temp) >= 10:
            del server_status_temp[0:5]
        if data['stateName'] == "Ingame":
            server_status_temp.append("going")
            return "going"
    except Exception as e:
        if server_status_temp != [] and server_status_temp[-1] == "going":
            server_status_temp.append("end")
            return "end"


def get_server_data():
    """
    获取服务器数据。

    Returns:
        Tuple: 包含全部玩家数据、第一队伍玩家数据和第二队伍玩家数据的元组。
    """
    return get_server_data_total(), get_server_data_team(1), get_server_data_team(2)


def get_server_data_total():
    """
    获取全部玩家数据。

    Returns:
        dict: 包含全部玩家数据的字典。
    """
    url = 'http://127.0.0.1:10086/Player/GetAllPlayerList'
    headers = {"Connection": "keep-alive"}
    timeout = 3
    response = requests.get(url, headers=headers, timeout=timeout)
    data = response.json()['data']
    return data


def get_server_data_team(index: int):
    """
    获取指定队伍的玩家数据。

    Args:
        index (int): 队伍索引，1表示第一队伍，2表示第二队伍。

    Returns:
        dict: 包含指定队伍玩家数据的字典。
    """
    url = f'http://127.0.0.1:10086/Player/GetTeam{index}PlayerList'
    headers = {"Connection": "keep-alive"}
    timeout = 3
    response = requests.get(url, headers=headers, timeout=timeout)
    return response.json()['data']


def get_server_info_data():
    """
    获取服务器信息数据。

    Returns:
        dict: 包含服务器信息数据的字典。
    """
    url = 'http://127.0.0.1:10086/Server/GetServerData'
    headers = {"Connection": "keep-alive"}
    timeout = 3
    response = requests.get(url, headers=headers, timeout=timeout)
    return response.json()['data']


def get_server_info():
    """
    获取服务器信息。

    Returns:
        str: 包含服务器名称、地图模式和两个队伍名称的字符串。
    """
    url = 'http://127.0.0.1:10086/Server/GetServerData'
    headers = {"Connection": "keep-alive"}
    timeout = 3
    response = requests.get(url, headers=headers, timeout=timeout)
    servername = response.json()['data']['name'][:20] + '\n'
    mapmode = response.json()['data']['gameMode2'] + '-' + response.json()['data']['mapName2'] + '\n'
    team = "队伍1:" + response.json()['data']["team1"]['name'] + "  队伍2:" + response.json()['data']["team2"]['name'] + '\n'
    server = servername + mapmode + team
    return server


def get_server_total_kd():
    """
    计算全部玩家的击杀数和死亡数。

    Returns:
        Tuple: 包含全部玩家的击杀数和死亡数的元组。
    """
    total_data = get_server_data_total()
    total_kill = sum([d.get('kill', 0) for d in total_data])
    total_death = sum([d.get('dead', 0) for d in total_data])
    return total_kill, total_death


def get_server_kd():
    """
    计算全部玩家、第一队伍和第二队伍的击杀数和死亡数。

    Returns:
        Tuple: 包含全部玩家的击杀数、死亡数，第一队伍的击杀数、死亡数，第二队伍的击杀数、死亡数的元组。
    """
    total_data, team1_data, team2_data = get_server_data()
    total_kill = sum([d.get('kill', 0) for d in total_data])
    total_death = sum([d.get('dead', 0) for d in total_data])
    team1_kill = sum([d.get('kill', 0) for d in team1_data])
    team1_death = sum([d.get('dead', 0) for d in team1_data])
    team2_kill = sum([d.get('kill', 0) for d in team2_data])
    team2_death = sum([d.get('dead', 0) for d in team2_data])
    return total_kill, total_death, team1_kill, team1_death, team2_kill, team2_death


def get_server_mean_rank():
    """
    计算全部玩家、第一队伍和第二队伍的平均排名。

    Returns:
        Tuple: 包含全部玩家的平均排名、第一队伍的平均排名、第二队伍的平均排名的元组。
    """
    total_data, team1_data, team2_data = get_server_data()
    total_rank = sum([d.get('rank', 0) for d in total_data]) / len(total_data)
    team1_rank = sum([d.get('rank', 0) for d in team1_data]) / len(team1_data)
    team2_rank = sum([d.get('rank', 0) for d in team2_data]) / len(team2_data)
    return int(total_rank), int(team1_rank), int(team2_rank)


def get_server_king():
    """
    获取全部玩家、第一队伍和第二队伍的击杀数最高的玩家和死亡数最高的玩家。

    Returns:
        Tuple: 包含全部玩家的击杀数最高的玩家、死亡数最高的玩家，第一队伍的击杀数最高的玩家、死亡数最高的玩家，
               第二队伍的击杀数最高的玩家、死亡数最高的玩家的元组。
    """
    total_data, team1_data, team2_data = get_server_data()
    total_kill_max, total_kill_king = get_king(total_data)
    team1_kill_max, team1_kill_king = get_king(team1_data)
    team2_kill_max, team2_kill_king = get_king(team2_data)
    total_death_max = max([d.get('dead', 0) for d in total_data])
    total_death_king = next(d.get('name', 'dsz') for d in total_data if d.get('dead', 0) == total_death_max)
    return total_kill_max, total_kill_king, total_death_max, total_death_king, team1_kill_max, team1_kill_king, team2_kill_max, team2_kill_king


def get_server_hot():
    """
    获取服务器中最热门的武器、手雷和刀具。

    Returns:
        Tuple: 包含最热门的武器、手雷和刀具的元组。
    """
    total_data = get_server_data_total()
    hot_weapon = get_hot(total_data, 'weaponS0')
    hot_grenade = get_hot(total_data, 'weaponS6')
    hot_knife = get_hot(total_data, 'weaponS7')
    return hot_weapon, hot_grenade, hot_knife


def get_server_num():
    """
    获取服务器中玩家的数量。

    Returns:
        Tuple: 包含全部玩家数量、第一队伍玩家数量和第二队伍玩家数量的元组。
    """
    total_data, team1_data, team2_data = get_server_data()
    return len(total_data), len(team1_data), len(team2_data)


def get_server_150():
    """
    获取服务器中排名为150的玩家数量。

    Returns:
        Tuple: 包含全部玩家排名为150的数量、第一队伍排名为150的数量和第二队伍排名为150的数量的元组。
    """
    total_data, team1_data, team2_data = get_server_data()
    total_150 = get_count(total_data, 'rank', 150)
    team1_150 = get_count(team1_data, 'rank', 150)
    team2_150 = get_count(team2_data, 'rank', 150)
    return total_150, team1_150, team2_150


def get_server_luck():
    """
    随机获取一个幸运玩家的名称。

    Returns:
        str: 幸运玩家的名称。
    """
    total_data = get_server_data_total()
    luck = total_data[random.randint(0, len(total_data) - 1)]['name']
    return luck


def get_server_playlist():
    """
    获取服务器中各个队伍的玩家列表。

    Returns:
        Tuple: 包含全部玩家列表、第一队伍玩家列表和第二队伍玩家列表的元组。
    """
    total_data, team1_data, team2_data = get_server_data()
    total_list = get_playerlist(total_data)
    team1_list = get_playerlist(team1_data)
    team2_list = get_playerlist(team2_data)
    return total_list, team1_list, team2_list


def get_server_all_report():
    """
    获取服务器的完整报告，包括服务器信息、玩家数量、平均等级、击杀数、死亡数、击杀王、狗带王、热门武器等信息。

    Returns:
        str: 服务器的完整报告。
    """
    report = "-" * 20 + "\n"
    server = get_server_info()
    total_kill, total_death, team1_kill, team1_death, team2_kill, team2_death = get_server_kd()
    total_rank, team1_rank, team2_rank = get_server_mean_rank()
    total_kill_max, total_kill_king, total_death_max, total_death_king, team1_kill_max, team1_kill_king, team2_kill_max, team2_kill_king = get_server_king()
    hot_weapon, hot_grenade, hot_knife = get_server_hot()
    total_num, team1_num, team2_num = get_server_num()
    total_150, team1_150, team2_150 = get_server_150()
    luck = get_server_luck()
    report += f"{server}服务器服内简报:\n"
    report += f"更新时间(`{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))}`)\n"
    report += f"共有玩家{total_num}名\n"
    report += f" 150数({total_150})服内平均等级{total_rank}\n"
    report += f"总击杀数为{total_kill}  总死亡数为{total_death}\n"
    report += f"击杀王为`{total_kill_king}`({total_kill_max})  狗带王为`{total_death_king}`({total_death_max})\n"
    report += f"幸运玩家为`{luck}`\n"
    report += f"热门主武器为{hot_weapon}\n"
    report += f"热门近战武器为{hot_knife}\n"
    report += f"热门投掷武器为{hot_grenade}\n"
    report += "-" * 20 + "\n"
    report += "队伍1信息:\n"
    report += f"人数{team1_num}  总击杀数{team1_kill}  总死亡数{team1_death}\n"
    report += f"平均等级{team1_rank}  150玩家数为{team1_150}\n"
    report += f"1队击杀王为`{team1_kill_king}`({team1_kill_max})\n"
    report += "-" * 20 + "\n"
    report += "队伍2信息:\n"
    report += f"人数{team2_num}  总击杀数{team2_kill}  总死亡数{team2_death}\n"
    report += f"平均等级{team2_rank}  150玩家数为{team2_150}\n"
    report += f"1队击杀王为`{team2_kill_king}`({team2_kill_max})\n\n"
    return report


def get_server_kd_report():
    """
    获取服务器的击杀数和死亡数报告。

    Returns:
        str: 服务器的击杀数和死亡数报告。
    """
    total_kill, total_death, team1_kill, team1_death, team2_kill, team2_death = get_server_kd()
    report = f"dsz report: 总击杀数为{total_kill}，总死亡数为{total_death}，队伍1击杀数为{team1_kill}，队伍1死亡数为{team1_death}，队伍2击杀数为{team2_kill}，队伍2死亡数为{team2_death}"
    return report


def get_server_rank_report():
    """
    获取服务器的平均等级报告。

    Returns:
        str: 服务器的平均等级报告。
    """
    total_rank, team1_rank, team2_rank = get_server_mean_rank()
    report = f"dsz report: 平均等级为{total_rank}，队伍1平级为{team1_rank}，队伍2平均等级为{team2_rank}"
    return report


def get_server_kill_total_report():
    """
    获取服务器的击杀王和狗带王报告。

    Returns:
        str: 服务器的击杀王和狗带王报告。
    """
    total_kill_max, total_kill_king, total_death_max, total_death_king, team1_kill_max, team1_kill_king, team2_kill_max, team2_kill_king = get_server_king()
    report = f"dsz report: 击杀王为{total_kill_king}（{total_kill_max}），狗带王为{total_death_king}（{total_death_max}）"
    return report


def get_server_kill_team_report():
    """
    获取服务器的队伍击杀王报告。

    Returns:
        str: 服务器的队伍击杀王报告。
    """
    total_kill_max, total_kill_king, total_death_max, total_death_king, team1_kill_max, team1_kill_king, team2_kill_max, team2_kill_king = get_server_king()
    report = f"dsz report: 队伍1击杀王为{team1_kill_king}（{team1_kill_max}），队伍2击杀王为{team2_kill_king}（{team2_kill_max}）"
    return report


def get_server_luck_report():
    """
    获取服务器的幸运玩家报告。

    Returns:
        str: 服务器的幸运玩家报告。
    """
    luck = get_server_luck()
    report = f"dsz report: {luck}被选为幸运玩家"
    return report


def get_server_hot_weapon_report():
    """
    获取服务器的热门主武器报告。

    Returns:
        str: 服务器的热门主武器报告。
    """
    hot_weapon, hot_grenade, hot_knife = get_server_hot()
    report = f"dsz report: 你知道吗？当前使用最多的主武器是{hot_weapon}"
    return report


def get_server_hot_grenade_report():
    """
    获取服务器的热门投掷物报告。

    Returns:
        str: 服务器的热门投掷物报告。
    """
    hot_weapon, hot_grenade, hot_knife = get_server_hot()
    report = f"dsz report: 你知道吗？当前使用最多的投掷物是{hot_grenade}"
    return report


def get_server_hot_knife_report():
    """
    获取服务器的热门刀报告。

    Returns:
        str: 服务器的热门刀报告。
    """
    hot_weapon, hot_grenade, hot_knife = get_server_hot()
    report = f"dsz report: 你知道吗？当前使用最多的刀是{hot_knife}"
    return report


def get_server_150_report():
    """
    获取服务器的150级玩家报告。

    Returns:
        str: 服务器的150级玩家报告。
    """
    total_150, team1_150, team2_150 = get_server_150()
    report = f"dsz report: 当前服务器有{total_150}位150级玩家，队伍1有{team1_150}位，队伍2有{team2_150}位"
    return report


def get_server_tips():
    """获取随机的服务器提示。

    返回：
        str: 随机的服务器提示。
    """
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
        "dsz tips:早期大栓服是抢攻为主的,但现在是以团队死斗为主",
        "dsz tips:或许你应该知道三炮打散ddf的故事",
        "dsz tips:dsz是什么意思,其实很简单就是dashuanzi(迫真",
        "dsz tips:ddf又是什么呢?黑暗地牢(x),打东风(yes)麻将馆",
        "dsz tips:如果你有什么好的建议请加入kook或qq与its联系",
        "dsz tips:参与暖服可以自助恰v",
        "dsz tips:世界第一刺刀是白露,不是英梨梨",
        "dsz tips:如果你只打算打狙,请一定要精通与此不然……",
        "dsz tips:为什么知道今天还没纯净大栓服呢?",
        "dsz tips:往脚下打信号弹会附带红温buff",
        "dsz tips:多打信号弹会有意外收获",
        "dsz tips:多往必经之路打信号弹烧人",
        "dsz tips:本服鼓励各种整活玩法,绊雷,毒气,筒子,蜘蛛人都可以",
        "dsz tips:你知道曾经活跃在ddf的mdw,lks,jwk复制人吗?"
    ]
    return tips[random.randint(0, len(tips) - 1)]


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
    return rules[random.randint(0, len(rules) - 1)]


def get_server_report_random():
    """随机获取服务器报告。

    Returns:
        str: 一个随机选择的服务器报告。
    """
    try:
        # 定义每个函数的权重
        report_funcs = [
            (get_server_kd_report, 2),
            (get_server_rank_report, 2),
            (get_server_kill_total_report, 2),
            (get_server_kill_team_report, 1),
            (get_server_luck_report, 1),
            (get_server_hot_weapon_report, 1),
            (get_server_hot_knife_report, 1),
            (get_server_150_report, 1),
            (get_server_tips, 2),
            (get_server_rules, 2),
            (get_server_join, 2)
        ]
        choices = []
        weights = []
        for func, weight in report_funcs:
            result = func()
            choices.append(result)
            weights.append(weight)
        result = random.choices(choices, weights=weights)[0]
    except Exception as e:
        report_funcs = [
            (get_server_tips, 2),
            (get_server_rules, 2),
            (get_server_join, 2)
        ]
        choices = []
        weights = []
        for func, weight in report_funcs:
            result = func()
            choices.append(result)
            weights.append(weight)
        result = random.choices(choices, weights=weights)[0]
    return result


def get_server_who_use_ban_weapon(banlist: list):
    """获取使用禁用武器的玩家列表。
    Args:
        banlist (list): 禁用武器列表。

    Returns:
        list: 包含使用禁用武器的玩家信息的列表。
            每个玩家信息是一个字典，包含以下键值对：
            - 玩家名称 (str)：玩家的名称。
            - pID (int)：玩家的pID。
            - 使用的禁用武器 (str)：玩家使用的禁用武器。
    """
    global ISINSERVER
    if ISINSERVER == False:
        return []
    total_data = get_server_data_total()
    if total_data is None:
        return []
    result_names = []
    for data in total_data:
        for i in range(8):
            weapon_key = "weaponS" + str(i)
            if weapon_key in data and data[weapon_key] != None and data[weapon_key]["name"] in banlist:
                result_names.append({data["name"]: [data["personaId"], data[weapon_key]["name"]]})
    return result_names

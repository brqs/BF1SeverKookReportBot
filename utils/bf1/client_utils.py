from loguru import logger
import requests
import time
import random


class Utils():
    def __init__(self) -> int or bool:
        self.gid_temp = []
        self.server_status_temp = []
        self.total_list, self.team1_list, self.team2_list = self.get_server_report_data(
            "playerlist")
        self.servername = "ddf"

    def get_gid(self):
        if len(self.gid_temp) > 50:
            del self.gid_temp[0:45]
        try:
            data = self.get_server_data("server")
            self.gid_temp.append(data["gameId"])
            return data["gameId"]
        except Exception as e:
            if len(self.gid_temp) != 0:
                return self.gid_temp[-1]
            else:
                return False

    def get_server_Ingame(self) -> bool:
        status = self.get_server_data("status")
        if status != False:
            if status["statusName"] == "Ingame":
                return True
            else:
                logger.error("bf1客户端未在服务器内")
                return False

    def get_server_status(self) -> str:
        try:
            total = self.get_server_data("total")
            isEnd = False
        except Exception as e:
            isEnd = True
        if len(self.server_status_temp) > 50:
            del self.server_status_temp[0:45]
        if isEnd:
            if len(self.server_status_temp) != 0 and self.server_status_temp[-1] == "going":
                self.server_status_temp.append("end")
                return "end"
        else:
            self.server_status_temp.append("going")
            return "going"

    def get_server_data(self, mode: str = "all") -> False or dict:
        url_total = 'http://127.0.0.1:10086/Player/GetAllPlayerList'
        url_server = 'http://127.0.0.1:10086/Server/GetServerData'
        url_status = "http://127.0.0.1:10086/Game/GetGameStatus"
        url_player = "http://127.0.0.1:10086/Player/GetLocalPlayer"
        url_chat="http://127.0.0.1:10086/Game/GetChatStatus"
        headers = {"Connection": "keep-alive"}
        timeout = 3
        try:
            if mode == "total":
                response = requests.get(
                    url_total, headers=headers, timeout=timeout)
                return response.json()['data']
            elif mode == "team":
                return self.get_server_data_team(1), self.get_server_data_team(2)
            elif mode == "server":
                response = requests.get(
                    url_server, headers=headers, timeout=timeout)
                return response.json()['data']
            elif mode == "all":
                response = requests.get(
                    url_total, headers=headers, timeout=timeout)
                return response.json()['data'], self.get_server_data_team(1), self.get_server_data_team(2)
            elif mode == "status":
                response = requests.get(
                    url_status, headers=headers, timeout=timeout)
                return response.json()['data']
            elif mode == "player":
                response = requests.get(
                    url_player, headers=headers, timeout=timeout)
                return response.json()['data']
            if mode == "chat":
                response = requests.get(
                    url_chat, headers=headers, timeout=timeout)
                return response.json()['data']
        except:
            logger.warning("未获取数据，请检查服务器是否开启")
            return False

    def get_server_data_team(self, index: int) -> dict:
        url = f'http://127.0.0.1:10086/Player/GetTeam{index}PlayerList'
        headers = {"Connection": "keep-alive"}
        timeout = 3
        response = requests.get(url, headers=headers, timeout=timeout)
        return response.json()['data']

    def get_server_report_data(self, mode: str) -> tuple or bool:
        total_data, team1_data, team2_data = self.get_server_data()
        self.servername = self.get_server_data("server")["name"][:10]
        try:
            if mode == 'kd':
                total_kill = sum([d.get('kill', 0) for d in total_data])
                total_death = sum([d.get('dead', 0) for d in total_data])
                team1_kill = sum([d.get('kill', 0) for d in team1_data])
                team1_death = sum([d.get('dead', 0) for d in team1_data])
                team2_kill = sum([d.get('kill', 0) for d in team2_data])
                team2_death = sum([d.get('dead', 0) for d in team2_data])
                return total_kill, total_death, team1_kill, team1_death, team2_kill, team2_death
            elif mode == "rank":
                total_rank = int(sum([d.get('rank', 0)
                                 for d in total_data]) / len(total_data))
                team1_rank = int(sum([d.get('rank', 0)
                                 for d in team1_data]) / len(team1_data))
                team2_rank = int(sum([d.get('rank', 0)
                                 for d in team2_data]) / len(team2_data))
                return total_rank, team1_rank, team2_rank
            elif mode == "king":
                total_kill_max, total_kill_king = self.find_metrics_in_dict(
                    "king", total_data)
                team1_kill_max, team1_kill_king = self.find_metrics_in_dict(
                    "king", team1_data)
                team2_kill_max, team2_kill_king = self.find_metrics_in_dict(
                    "king", team2_data)
                total_death_max = max([d.get('dead', 0) for d in total_data])
                total_death_king = next(d.get('name', 'dsz') for d in total_data if d.get(
                    'dead', 0) == total_death_max)
                return total_kill_max, total_kill_king, total_death_max, total_death_king, team1_kill_max, team1_kill_king, team2_kill_max, team2_kill_king
            elif mode == "hot":
                hot_weapon = self.find_metrics_in_dict(
                    "hot", total_data, 'weaponS0')
                hot_grenade = self.find_metrics_in_dict(
                    "hot", total_data, 'weaponS6')
                hot_knife = self.find_metrics_in_dict(
                    "hot", total_data, 'weaponS7')
                return hot_weapon, hot_grenade, hot_knife
            elif mode == "num":
                return len(total_data), len(team1_data), len(team2_data)
            elif mode == "150":
                total_150 = self.find_metrics_in_dict(
                    "count", total_data, 'rank', 150)
                team1_150 = self.find_metrics_in_dict(
                    "count", team1_data, 'rank', 150)
                team2_150 = self.find_metrics_in_dict(
                    "count", team2_data, 'rank', 150)
                return total_150, team1_150, team2_150
            elif mode == "playerlist":
                total_list = self.find_metrics_in_dict(
                    "playerlist", total_data)
                team1_list = self.find_metrics_in_dict(
                    "playerlist", team1_data)
                team2_list = self.find_metrics_in_dict(
                    "playerlist", team2_data)
                return total_list, team1_list, team2_list
            elif mode == "info":
                server_info = self.get_server_data("server")
                servername = server_info['name'][:20] + '\n'
                mapmode = server_info['gameMode2'] + \
                    '-' + server_info['mapName2'] + '\n'
                team = "队伍1:" + server_info["team1"]['name'] + \
                    "  队伍2:" + server_info["team2"]['name'] + '\n'
                server = servername + mapmode + team
                return server
            elif mode == "luck":
                luck = total_data[random.randint(
                    0, len(total_data) - 1)]['name']
                return luck
        except:
            logger.warning("查找出错,请检查api信息")
            return False

    def get_server_report(self, mode: str = "random") -> bool or str:
        try:
            server = self.get_server_report_data("info")
            total_kill, total_death, team1_kill, team1_death, team2_kill, team2_death = self.get_server_report_data(
                "kd")
            total_rank, team1_rank, team2_rank = self.get_server_report_data(
                "rank")
            total_kill_max, total_kill_king, total_death_max, total_death_king, team1_kill_max, team1_kill_king, team2_kill_max, team2_kill_king = self.get_server_report_data(
                "king")
            hot_weapon, hot_grenade, hot_knife = self.get_server_report_data(
                "hot")
            total_num, team1_num, team2_num = self.get_server_report_data(
                "num")
            total_150, team1_150, team2_150 = self.get_server_report_data(
                "150")
            luck = self.get_server_report_data("luck")
            report = []
            if mode == "all":
                report = "-" * 20 + "\n"
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
            elif mode == "random":
                report.append(
                    f"dsz report: 总击杀数为{total_kill}，总死亡数为{total_death}，队伍1击杀数为{team1_kill}，队伍1死亡数为{team1_death}，队伍2击杀数为{team2_kill}，队伍2死亡数为{team2_death}")
                report.append(
                    f"dsz report: 平均等级为{total_rank}，队伍1平级为{team1_rank}，队伍2平均等级为{team2_rank}")
                report.append(
                    f"dsz report: 击杀王为{total_kill_king}({total_kill_max})，狗带王为{total_death_king}({total_death_max})")
                report.append(
                    f"dsz report: 队伍1击杀王为{team1_kill_king}({team1_kill_max})，队伍2击杀王为{team2_kill_king}({team2_kill_max})")
                report.append(f"dsz report: {luck}被选为幸运玩家")
                report.append(f"dsz report: 你知道吗？当前使用最多的主武器是{hot_weapon}")
                report.append(f"dsz report: 你知道吗？当前使用最多的投掷物是{hot_grenade}")
                report.append(f"dsz report: 你知道吗？当前使用最多的刀是{hot_knife}")
                report.append(
                    f"dsz report: 当前服务器有{total_150}位150级玩家，队伍1有{team1_150}位，队伍2有{team2_150}位")
                return report[random.randint(0, len(report) - 1)]
        except:
            return False

    def get_server_tips(self) -> str:
        tips = [
            "dsz tips:服务器ddf1禁用炸药,1903exp,空爆迫击炮,闪光",
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

    def get_server_rules(self) -> str:
        rules = [
            "dsz rules:服务器ddf1禁用炸药,1903exp,空爆迫击炮,闪光,其他武器无限制",
            "dsz rules:如果你对该机器人功能感兴趣请加入ddf kook服务器:https://kook.top/A17StS",
            "dsz rules:出现外挂,请加入qq群或者kook向管理员反馈",
            "dsz rules:150请自觉平衡不要抱团捞薯",
            "dsz rules:如果你希望加入ddf管理团队请加入qq群和kook"
        ]
        return rules[random.randint(0, len(rules) - 1)]

    def get_server_join(self) -> str:
        join = [
            "dsz invite:ddf服务器QQ群号838082738,ddf kook服务器:https://kook.top/A17StS",
            "dsz invite:如果你对该机器人功能感兴趣请加入ddf kook服务器:https://kook.top/A17StS",
        ]
        return join[random.randint(0, len(join) - 1)]

    def get_server_report_random(self) -> str:
        try:
            # 定义每个函数的权重
            report_funcs = [
                (self.get_server_report, 6),
                (self.get_server_tips, 2),
                (self.get_server_rules, 2),
                (self.get_server_join, 2)
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
                (self.get_server_tips, 2),
                (self.get_server_rules, 2),
                (self.get_server_join, 2)
            ]
            choices = []
            weights = []
            for func, weight in report_funcs:
                result = func()
                choices.append(result)
                weights.append(weight)
            result = random.choices(choices, weights=weights)[0]
        return result

    def find_metrics_in_dict(self, mode: str, lst: list, key: str = None, value: str = None) -> tuple:
        if mode == 'king':
            max_kill = max([d.get('kill', 0) for d in lst])
            result = next(d.get('name', 'dsz')
                          for d in lst if d.get('kill', 0) == max_kill)
            return max_kill, result
        elif mode == 'hot':
            hot_counts = {}
            for d in lst:
                if d[key] is None:
                    continue
                if d[key]['name'] != "":
                    hot_counts[d[key]['name']] = hot_counts.get(
                        d[key]['name'], 0) + 1
            maxhot_count = max(hot_counts.values())
            result = next(
                d[key]['name']
                for d in lst
                if d[key] is not None and d[key]['name'] == max(hot_counts, key=hot_counts.get)
            )
            return result
        elif mode == "count":
            count = sum(1 for d in lst if d.get(key) == value)
            return count
        elif mode == "playerlist":
            result_lst = [
                {k: d[k] for k in ['name', 'rank', 'kill', 'dead']}
                for d in lst
                if all(key in d for key in ['name', 'rank', 'kill', 'dead'])
            ]
            return result_lst

    def get_server_who_use_ban_weapon(self, banlist: list):
        """获取使用禁用武器的玩家列表。
        Args:
            banlist (list): 禁用武器列表。
        ["炸药","特殊载具 空爆迫击炮","M1903（实验）","信号枪（闪光）"]
        Returns:
            list: 包含使用禁用武器的玩家信息的列表。
                每个玩家信息是一个字典，包含以下键值对：
                - 玩家名称 (str)：玩家的名称。
                - pID (int)：玩家的pID。
                - 使用的禁用武器 (str)：玩家使用的禁用武器。
        """
        total_data = self.get_server_data("total")
        if total_data is None:
            return []
        result_names = []
        for data in total_data:
            for i in range(8):
                weapon_key = "weaponS" + str(i)
                if weapon_key in data and data[weapon_key] != None and data[weapon_key]["name"] in banlist:
                    result_names.append(
                        {data["name"]: [data["personaId"], data[weapon_key]["name"]]})
        return result_names

    def get_team_new(self):
        try:
            total_list, team1_list, team2_list = self.get_server_report_data(
                "playerlist")
        except Exception as e:
            logger.warning("服务器加载中或未开启")
            return [], [], [], self.total_list, self.team1_list, self.team2_list
        # 获取 team1 和 team2 中的玩家名称集合
        team1_names = set(player['name'] for player in self.team1_list)
        team2_names = set(player['name'] for player in self.team2_list)
        total_names = set(player['name'] for player in self.total_list)
        new_team1_names = set(player['name'] for player in team1_list)
        new_team2_names = set(player['name'] for player in team2_list)
        new_total_names = set(player['name'] for player in total_list)
        # 计算新加入玩家的名称集合和更换队伍玩家的名称集合
        new_players = new_total_names - total_names
        left_players = total_names - new_total_names
        # 打印新加入玩家的 ID 和等级
        new_player_lst = []
        for player in total_list:
            if player['name'] in new_players:
                new_player_lst.append([player['name'], player['rank']])
        left_player_lst = []
        for player in self.total_list:
            if player['name'] in left_players:
                left_player_lst.append(
                    [player['name'], player['rank'], player['kill'], player['dead']])
        swapped_players1 = team1_names & new_team2_names
        swapped_players2 = team2_names & new_team1_names
        swapped_players_lst = []
        for player in total_list:
            if player['name'] in swapped_players1:
                swapped_players_lst.append(
                    [player['name'], player['rank'], "1"])
            elif player['name'] in swapped_players2:
                swapped_players_lst.append(
                    [player['name'], player['rank'], "2"])
        return new_player_lst, left_player_lst, swapped_players_lst, total_list, team1_list, team2_list

    def player_list_changes_report(self, mode=str):
        new_player_lst, left_player_lst, swapped_players_lst, total_list, team1_list, team2_list = self.get_team_new()
        if mode == "new":
            if new_player_lst != []:
                return "\n".join(f"`{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))}`玩家`{i[0]}`等级`{i[1]}`加入服务器`{self.servername}`" for i in new_player_lst)
            else:
                return False
        elif mode == "left":
            if left_player_lst != []:
                return "\n".join(f"`{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))}`玩家`{i[0]}`等级`{i[1]}`击杀`{i[3]}`名薯条后心满意足的离开了服务器`{self.servername}`" for i in left_player_lst)
            else:
                return False
        elif mode == "swap":
            if swapped_players_lst != []:
                return "\n".join(f"`{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))}`玩家`{i[0]}`等级`{i[1]}`由队伍{1 if i[2]=='1' else 2}==>队伍{2 if i[2]=='1' else 1}" for i in swapped_players_lst)
            else:
                return False
        elif mode == "all":
            return self.player_list_changes_report("new"), self.player_list_changes_report("left"), self.player_list_changes_report("swap")
        elif mode == "update":
            self.total_list, self.team1_list, self.team2_list = total_list, team1_list, team2_list


Clientutils = Utils()
# time.sleep(60)
# print(Clientutils.get_team_new()[0:3])
# print(Clientutils.player_list_changes_report("new"))
# print(Clientutils.player_list_changes_report("left"))
# print(Clientutils.player_list_changes_report("swap"))
# print(Clientutils.player_list_changes_report("all"))

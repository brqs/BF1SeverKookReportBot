import datetime
from typing import Union, List, Tuple, Dict, Any

from loguru import logger
from sqlalchemy import select, func

from utils.bf1.database.tables import orm, Bf1PlayerBind, Bf1Account, Bf1Server, Bf1Group, Bf1GroupBind, Bf1MatchCache, \
    Bf1ServerVip, Bf1ServerBan, Bf1ServerAdmin, Bf1ServerOwner, Bf1ServerPlayerCount, Bf1ManagerLog, Bf1GroupAdmin, \
    Bf1Import
import uuid
import json


class bf1_db:

    # TODO:
    #  BF1账号相关
    #  读：
    #  根据pid获取玩家信息
    #  根据pid获取session
    #  写：
    #  初始化写入玩家pid
    #  根据pid写入remid和sid
    #  根据pid写入session
    @staticmethod
    async def get_bf1account_by_pid(pid: int) -> dict:
        """
        根据pid获取玩家信息
        :param pid: 玩家persona_id(pid)
        :return: 有结果时,返回dict,无结果时返回None
        """
        # 获取玩家persona_id、user_id、name、display_name
        if account := await orm.fetch_one(
                select(
                    Bf1Account.persona_id, Bf1Account.user_id, Bf1Account.name, Bf1Account.display_name,
                    Bf1Account.remid, Bf1Account.sid, Bf1Account.session
                ).where(
                    Bf1Account.persona_id == pid
                )
        ):
            return {
                "pid": account[0],
                "uid": account[1],
                "name": account[2],
                "display_name": account[3],
                "remid": account[4],
                "sid": account[5],
                "session": account[6]
            }
        else:
            return None

    @staticmethod
    async def get_session_by_pid(pid: int) -> str:
        if account := await orm.fetch_one(select(Bf1Account.session).where(Bf1Account.persona_id == pid)):
            return account[0]
        else:
            return None

    @staticmethod
    async def update_bf1account(
            pid: int, display_name: str, uid: int = None, name: str = None,
            remid: str = None, sid: str = None, session: str = None
    ) -> bool:
        if not pid:
            logger.error("pid不能为空!")
            return False
        data = {
            "persona_id": pid,
        }
        if uid:
            data["user_id"] = uid
        if name:
            data["name"] = name
        if display_name:
            data["display_name"] = display_name
        if remid:
            data["remid"] = remid
        if sid:
            data["sid"] = sid
        if session:
            data["session"] = session
        await orm.insert_or_update(
            table=Bf1Account,
            data=data,
            condition=[
                Bf1Account.persona_id == pid
            ]
        )
        return True

    @staticmethod
    async def update_bf1account_loginInfo(
            pid: int, remid: str = None, sid: str = None, session: str = None
    ) -> bool:
        """
        根据pid写入remid和sid、session
        :param pid: 玩家persona_id(pid)
        :param remid: cookie中的remid
        :param sid: cookie中的sid
        :param session: 登录后的session
        :return: None
        """
        data = {"persona_id": pid}
        if remid:
            data["remid"] = remid
        if sid:
            data["sid"] = sid
        if session:
            data["session"] = session
        await orm.insert_or_update(
            table=Bf1Account,
            data=data,
            condition=[
                Bf1Account.persona_id == pid
            ]
        )
        return True

    # TODO:
    #  绑定相关
    #  读:
    #  根据kook获取绑定的pid
    #  根据pid获取绑定的kook
    #  写:
    #  写入绑定信息 kook-pid

    @staticmethod
    async def get_pid_by_kook(kook: int) -> int:
        """
        根据kook获取绑定的pid
        :param kook: kook号
        :return: 绑定的pid,没有绑定时返回None
        """
        if bind := await orm.fetch_one(select(Bf1PlayerBind.persona_id).where(Bf1PlayerBind.kook == kook)):
            return bind[0]
        else:
            return None

    @staticmethod
    async def get_kook_by_pid(pid: int) -> list:
        """
        根据pid获取绑定的kook
        :param pid: 玩家persona_id(pid)
        :return: 返回一个list,里面是绑定的kook号,没有绑定时返回None
        """
        if bind := await orm.fetch_all(select(Bf1PlayerBind.kook).where(Bf1PlayerBind.persona_id == pid)):
            return [i[0] for i in bind]
        else:
            return None

    @staticmethod
    async def bind_player_kook(kook: int, pid: int) -> bool:
        """
        写入绑定信息 kook-pid
        :param kook: kook号
        :param pid: 玩家persona_id(pid)
        :return: True
        """
        await orm.insert_or_update(
            table=Bf1PlayerBind,
            data={
                "persona_id": pid,
                "kook": kook
            },
            condition=[
                Bf1PlayerBind.kook == kook
            ]
        )

    # TODO:
    #  服务器相关
    #  读:
    #  根据serverid/guid获取对应信息如gameid、
    #  写:
    #  从getFullServerDetails获取并写入服务器信息

    @staticmethod
    async def update_serverInfo(
            serverName: str, serverId: str, guid: str, gameId: int,
            createdDate: datetime.datetime, expirationDate: datetime.datetime, updatedDate: datetime.datetime
    ) -> bool:
        await orm.insert_or_update(
            table=Bf1Server,
            data={
                "serverName": serverName,
                "serverId": serverId,
                "persistedGameId": guid,
                "gameId": gameId,
                "createdDate": createdDate,
                "expirationDate": expirationDate,
                "updatedDate": updatedDate,
                "record_time": datetime.datetime.now()
            },
            condition=[
                Bf1Server.serverId == serverId
            ]
        )
        return True

    @staticmethod
    async def update_serverInfoList(
            server_info_list: List[Tuple[str, str, str, int, datetime.datetime, datetime.datetime, datetime.datetime]]
    ) -> bool:
        # 构造要插入或更新的记录列表
        info_records = []
        player_records = []
        for serverName, serverId, guid, gameId, serverBookmarkCount, createdDate, expirationDate, updatedDate, playerCurrent, playerMax, playerQueue, playerSpectator in server_info_list:
            record = {
                "serverName": serverName,
                "serverId": serverId,
                "persistedGameId": guid,
                "gameId": gameId,
                "createdDate": createdDate,
                "expirationDate": expirationDate,
                "updatedDate": updatedDate,
                "record_time": datetime.datetime.now()
            }
            info_records.append(record)
            record = {
                "serverId": serverId,
                "playerCurrent": playerCurrent,
                "playerMax": playerMax,
                "playerQueue": playerQueue,
                "playerSpectator": playerSpectator,
                "time": datetime.datetime.now(),
                "serverBookmarkCount": serverBookmarkCount,
            }
            player_records.append(record)

        # 插入或更新记录
        await orm.insert_or_update_batch(
            table=Bf1Server,
            data_list=info_records,
            conditions_list=[(Bf1Server.serverId == record["serverId"],) for record in info_records]
        )
        await orm.add_batch(
            table=Bf1ServerPlayerCount,
            data_list=player_records
        )

    @staticmethod
    async def get_serverInfo_byServerId(
            serverId: str
    ) -> Bf1Server:
        if server := await orm.fetch_one(select(
                Bf1Server.serverName, Bf1Server.serverId, Bf1Server.persistedGameId, Bf1Server.gameId,
        ).where(Bf1Server.serverId == serverId)):
            result = {

            }
            return result
        else:
            return None

    @staticmethod
    async def get_all_serverInfo() -> list:
        if servers := await orm.fetch_all(
                select(
                    Bf1Server.serverId, Bf1Server.expirationDate,
                )
        ):
            result = []
            for server in servers:
                result.append({

                })
            return result
        else:
            return None

    @staticmethod
    async def update_serverVip(
            serverId: str, persona_id: int, display_name: str
    ) -> bool:
        await orm.insert_or_update(
            table=Bf1ServerVip,
            data={
                "serverId": serverId,
                "persona_id": persona_id,
                "display_name": display_name,
                "time": datetime.datetime.now(),
            },
            condition=[
                Bf1ServerVip.serverId == serverId,
                Bf1ServerVip.personaId == persona_id
            ]
        )
        return True

    @staticmethod
    async def get_playerVip(persona_id: int) -> int:
        """
        查询玩家的VIP数量
        :param persona_id: 玩家persona_id(pid)
        :return: VIP数量
        """
        if result := await orm.fetch_all(
                select(Bf1ServerVip.serverId).where(
                    Bf1ServerVip.personaId == persona_id
                )
        ):
            return len([i[0] for i in result])
        else:
            return 0

    @staticmethod
    async def get_playerVipServerList(persona_id: int) -> list:
        """
        查询玩家的VIP服务器列表
        :param persona_id: 玩家persona_id(pid)
        :return: VIP服务器列表
        """
        if result := await orm.fetch_all(
                select(Bf1ServerVip.serverId).where(
                    Bf1ServerVip.personaId == persona_id
                )
        ):
            server_list = []
            # 根据serverId查询serverName
            for item in result:
                serverId = item[0]
                if server := await orm.fetch_one(
                        select(Bf1Server.serverName).where(
                            Bf1Server.serverId == serverId
                        )
                ):
                    server_list.append(server[0])
            return server_list
        else:
            return []

    @staticmethod
    async def get_allServerPlayerVipList() -> list:
        """
        查询所有玩家拥有的VIP数量
        :return: 服务器VIP列表
        """
        # 查询整个表
        if result := await orm.fetch_all(
                select(Bf1ServerVip.serverId, Bf1ServerVip.personaId, Bf1ServerVip.displayName)
        ):
            # 挑选出所有的pid和对应dName,放在list中,然后按照server_list的数量排序
            # data = [
            #     {
            #         "pid": 123,
            #         "displayName": "xxx",
            #         "server_list": []
            #     }
            # ]
            data = []
            for item in result:
                serverId = item[0]
                pid = item[1]
                dName = item[2]
                # 如果data中已经存在该pid,则直接添加serverId
                if pid in [i["pid"] for i in data]:
                    for i in data:
                        if i["pid"] == pid:
                            i["server_list"].append(serverId)
                else:
                    data.append({
                        "pid": pid,
                        "displayName": dName,
                        "server_list": [serverId]
                    })
            # 按照server_list的数量排序
            data.sort(key=lambda x: len(x["server_list"]), reverse=True)
            return data
        else:
            return []

    @staticmethod
    async def update_serverVipList(
            vip_dict: Dict[int, Dict[str, Any]]
    ) -> bool:
        update_list = []
        delete_list = []
        # 查询所有记录
        all_records = await orm.fetch_all(
            select(Bf1ServerVip.serverId, Bf1ServerVip.personaId, Bf1ServerVip.displayName).where(
                Bf1ServerVip.serverId.in_(vip_dict.keys())
            )
        )
        all_records = {f"{record[0]}-{record[1]}": record[2] for record in all_records}
        now_records = {f"{serverId}-{record['personaId']}": record["displayName"] for serverId, records in
                       vip_dict.items() for
                       record in records}
        # 如果数据库中的记录不在现在的记录中,则删除
        # 如果数据库中的记录在现在的记录中,则更新对应pid下变化的display_name
        for record in all_records:
            if record not in now_records:
                delete_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1]
                })
            elif all_records[record] != now_records[record]:
                update_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1],
                    "displayName": now_records[record],
                    "time": datetime.datetime.now(),
                })
        # 如果现在的记录不在数据库中,则插入
        for record in now_records:
            if record not in all_records:
                update_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1],
                    "displayName": now_records[record],
                    "time": datetime.datetime.now(),
                })
        # 更新
        await orm.insert_or_update_batch(
            table=Bf1ServerVip,
            data_list=update_list,
            conditions_list=[
                (Bf1ServerVip.serverId == record["serverId"], Bf1ServerVip.personaId == record["personaId"]) for
                record in update_list]
        )
        # 删除
        await orm.delete_batch(
            table=Bf1ServerVip,
            conditions_list=[
                (Bf1ServerVip.serverId == record["serverId"], Bf1ServerVip.personaId == record["personaId"]) for
                record in delete_list]
        )

    @staticmethod
    async def update_serverBan(
            serverId: str, persona_id: int, display_name: str
    ) -> bool:
        await orm.insert_or_update(
            table=Bf1ServerBan,
            data={
                "serverId": serverId,
                "persona_id": persona_id,
                "display_name": display_name,
                "time": datetime.datetime.now(),
            },
            condition=[
                Bf1ServerBan.serverId == serverId,
                Bf1ServerBan.personaId == persona_id
            ]
        )
        return True

    @staticmethod
    async def get_playerBan(persona_id: int) -> int:
        """
        查询玩家的Ban数量
        :param persona_id: 玩家persona_id(pid)
        :return: Ban数量
        """
        if result := await orm.fetch_all(
                select(Bf1ServerBan.serverId).where(
                    Bf1ServerBan.personaId == persona_id
                )
        ):
            return len([i[0] for i in result])
        else:
            return 0

    @staticmethod
    async def get_playerBanServerList(persona_id: int) -> list:
        """
        查询玩家的Ban服务器列表
        :param persona_id: 玩家persona_id(pid)
        :return: Ban服务器列表
        """
        if result := await orm.fetch_all(
                select(Bf1ServerBan.serverId).where(
                    Bf1ServerBan.personaId == persona_id
                )
        ):
            server_list = []
            # 根据serverId查询serverName
            for item in result:
                serverId = item[0]
                if server := await orm.fetch_one(
                        select(Bf1Server.serverName).where(
                            Bf1Server.serverId == serverId
                        )
                ):
                    server_list.append(server[0])
            return server_list
        else:
            return []

    @staticmethod
    async def get_allServerPlayerBanList() -> list:
        """
        获取所有服务器的玩家Ban列表
        :return: {"pid": pid, "displayName": displayName, "server_list": [serverId, serverId]}
        """
        if result := await orm.fetch_all(
                select(Bf1ServerBan.serverId, Bf1ServerBan.personaId, Bf1ServerBan.displayName)
        ):
            data = {}
            for item in result:
                serverId = item[0]
                pid = item[1]
                displayName = item[2]
                if pid not in data:
                    data[pid] = {
                        "displayName": displayName,
                        "server_list": [serverId]
                    }
                else:
                    data[pid]["server_list"].append(serverId)
            # 按照server_list的数量排序
            data = [{"pid": pid, **value} for pid, value in data.items()]
            data.sort(key=lambda x: len(x["server_list"]), reverse=True)
            return data
        else:
            return []

    @staticmethod
    async def update_serverBanList(
            ban_dict: Dict[int, Dict[str, Any]]
    ) -> bool:
        update_list = []
        delete_list = []
        # 查询所有记录
        all_records = await orm.fetch_all(
            select(Bf1ServerBan.serverId, Bf1ServerBan.personaId, Bf1ServerBan.displayName).where(
                Bf1ServerBan.serverId.in_(ban_dict.keys())
            )
        )
        all_records = {f"{record[0]}-{record[1]}": record[2] for record in all_records}
        now_records = {f"{serverId}-{record['personaId']}": record["displayName"] for serverId, records in
                       ban_dict.items() for
                       record in records}
        # 如果数据库中的记录不在现在的记录中,则删除
        # 如果数据库中的记录在现在的记录中,则更新对应pid下变化的display_name
        for record in all_records:
            if record not in now_records:
                delete_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1]
                })
            elif all_records[record] != now_records[record]:
                update_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1],
                    "displayName": now_records[record],
                    "time": datetime.datetime.now(),
                })
        # 如果现在的记录不在数据库中,则插入
        for record in now_records:
            if record not in all_records:
                update_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1],
                    "displayName": now_records[record],
                    "time": datetime.datetime.now(),
                })
        # 更新
        await orm.insert_or_update_batch(
            table=Bf1ServerBan,
            data_list=update_list,
            conditions_list=[
                (Bf1ServerBan.serverId == record["serverId"], Bf1ServerBan.personaId == record["personaId"]) for
                record in update_list]
        )
        # 删除
        await orm.delete_batch(
            table=Bf1ServerBan,
            conditions_list=[
                (Bf1ServerBan.serverId == record["serverId"], Bf1ServerBan.personaId == record["personaId"]) for
                record in delete_list]
        )

    @staticmethod
    async def update_serverAdmin(
            serverId: str, persona_id: int, display_name: str
    ) -> bool:
        await orm.insert_or_update(
            table=Bf1ServerAdmin,
            data={
                "serverId": serverId,
                "persona_id": persona_id,
                "display_name": display_name,
                "time": datetime.datetime.now(),
            },
            condition=[
                Bf1ServerAdmin.serverId == serverId,
                Bf1ServerAdmin.personaId == persona_id
            ]
        )
        return True

    @staticmethod
    async def get_playerAdmin(persona_id: int) -> int:
        """
        查询玩家的Admin数量
        :param persona_id: 玩家persona_id(pid)
        :return: Admin数量
        """
        if result := await orm.fetch_all(
                select(Bf1ServerAdmin.serverId).where(
                    Bf1ServerAdmin.personaId == persona_id
                )
        ):
            return len([i[0] for i in result])
        else:
            return 0

    @staticmethod
    async def get_playerAdminServerList(persona_id: int) -> list:
        """
        查询玩家的Admin服务器列表
        :param persona_id: 玩家persona_id(pid)
        :return: Admin服务器列表
        """
        if result := await orm.fetch_all(
                select(Bf1ServerAdmin.serverId).where(
                    Bf1ServerAdmin.personaId == persona_id
                )
        ):
            server_list = []
            # 根据serverId查询serverName
            for item in result:
                serverId = item[0]
                if server := await orm.fetch_one(
                        select(Bf1Server.serverName).where(
                            Bf1Server.serverId == serverId
                        )
                ):
                    server_list.append(server[0])
            return server_list
        else:
            return []

    @staticmethod
    async def get_allServerPlayerAdminList() -> list:
        """
        查询所有服务器的玩家Admin列表
        :return: 所有服务器的玩家Admin列表
        """
        if result := await orm.fetch_all(
                select(Bf1ServerAdmin.serverId, Bf1ServerAdmin.personaId, Bf1ServerAdmin.displayName)
        ):
            data = []
            for item in result:
                serverId = item[0]
                pid = item[1]
                dName = item[2]
                # 如果data中已经存在该pid,则直接添加serverId
                if pid in [i["pid"] for i in data]:
                    for i in data:
                        if i["pid"] == pid:
                            i["server_list"].append(serverId)
                else:
                    data.append({
                        "pid": pid,
                        "displayName": dName,
                        "server_list": [serverId]
                    })
            # 按照server_list的数量排序
            data.sort(key=lambda x: len(x["server_list"]), reverse=True)
            return data
        else:
            return []

    @staticmethod
    async def update_serverAdminList(
            admin_dict: Dict[int, Dict[str, Any]]
    ) -> bool:
        update_list = []
        delete_list = []
        # 查询所有记录
        all_records = await orm.fetch_all(
            select(Bf1ServerAdmin.serverId, Bf1ServerAdmin.personaId, Bf1ServerAdmin.displayName).where(
                Bf1ServerAdmin.serverId.in_(admin_dict.keys())
            )
        )
        all_records = {f"{record[0]}-{record[1]}": record[2] for record in all_records}
        now_records = {f"{serverId}-{record['personaId']}": record["displayName"] for serverId, records in
                       admin_dict.items() for
                       record in records}
        # 如果数据库中的记录不在现在的记录中,则删除
        # 如果数据库中的记录在现在的记录中,则更新对应pid下变化的display_name
        for record in all_records:
            if record not in now_records:
                delete_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1]
                })
            elif all_records[record] != now_records[record]:
                update_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1],
                    "displayName": now_records[record],
                    "time": datetime.datetime.now(),
                })
        # 如果现在的记录不在数据库中,则插入
        for record in now_records:
            if record not in all_records:
                update_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1],
                    "displayName": now_records[record],
                    "time": datetime.datetime.now(),
                })
        # 更新
        await orm.insert_or_update_batch(
            table=Bf1ServerAdmin,
            data_list=update_list,
            conditions_list=[
                (Bf1ServerAdmin.serverId == record["serverId"], Bf1ServerAdmin.personaId == record["personaId"]) for
                record in update_list]
        )
        # 删除
        await orm.delete_batch(
            table=Bf1ServerAdmin,
            conditions_list=[
                (Bf1ServerAdmin.serverId == record["serverId"], Bf1ServerAdmin.personaId == record["personaId"]) for
                record in delete_list]
        )

    @staticmethod
    async def update_serverOwner(
            serverId: str, persona_id: int, display_name: str
    ) -> bool:
        await orm.insert_or_update(
            table=Bf1ServerOwner,
            data={
                "serverId": serverId,
                "persona_id": persona_id,
                "display_name": display_name,
                "time": datetime.datetime.now(),
            },
            condition=[
                Bf1ServerOwner.serverId == serverId,
                Bf1ServerOwner.personaId == persona_id
            ]
        )
        return True

    @staticmethod
    async def get_playerOwner(persona_id: int) -> int:
        """
        查询玩家的Owner数量
        :param persona_id: 玩家persona_id(pid)
        :return: Owner数量
        """
        if result := await orm.fetch_all(
                select(Bf1ServerOwner.serverId).where(
                    Bf1ServerOwner.personaId == persona_id
                )
        ):
            return len([i[0] for i in result])
        else:
            return 0

    @staticmethod
    async def get_playerOwnerServerList(persona_id: int) -> list:
        """
        查询玩家的Owner服务器列表
        :param persona_id: 玩家persona_id(pid)
        :return: Owner服务器列表
        """
        if result := await orm.fetch_all(
                select(Bf1ServerOwner.serverId).where(
                    Bf1ServerOwner.personaId == persona_id
                )
        ):
            server_list = []
            # 根据serverId查询serverName
            for item in result:
                serverId = item[0]
                if server := await orm.fetch_one(
                        select(Bf1Server.serverName).where(
                            Bf1Server.serverId == serverId
                        )
                ):
                    server_list.append(server[0])
            return server_list
        else:
            return []

    @staticmethod
    async def get_allServerPlayerOwnerList() -> list:
        """
        查询所有服务器的Owner列表
        :return: 所有服务器的Owner列表
        """
        if result := await orm.fetch_all(
                select(Bf1ServerOwner.serverId, Bf1ServerOwner.personaId, Bf1ServerOwner.displayName)
        ):
            data = []
            for item in result:
                serverId = item[0]
                pid = item[1]
                dName = item[2]
                # 如果data中已经存在该pid,则直接添加serverId
                if pid in [i["pid"] for i in data]:
                    for i in data:
                        if i["pid"] == pid:
                            i["server_list"].append(serverId)
                else:
                    data.append({
                        "pid": pid,
                        "displayName": dName,
                        "server_list": [serverId]
                    })
            # 按照server_list的数量排序
            data.sort(key=lambda x: len(x["server_list"]), reverse=True)
            return data
        else:
            return []

    @staticmethod
    async def update_serverOwnerList(
            owner_dict: Dict[int, Dict[str, Any]]
    ) -> bool:
        update_list = []
        delete_list = []
        # 查询所有记录
        all_records = await orm.fetch_all(
            select(Bf1ServerOwner.serverId, Bf1ServerOwner.personaId, Bf1ServerOwner.displayName).where(
                Bf1ServerOwner.serverId.in_(owner_dict.keys())
            )
        )
        all_records = {f"{record[0]}-{record[1]}": record[2] for record in all_records}
        now_records = {
            f"{serverId}-{record['personaId']}": record["displayName"]
            for serverId, records in owner_dict.items() for record in records
        }
        # 如果数据库中的记录不在现在的记录中,则删除
        # 如果数据库中的记录在现在的记录中,则更新对应pid下变化的display_name
        for record in all_records:
            if record not in now_records:
                delete_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1]
                })
            elif all_records[record] != now_records[record]:
                update_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1],
                    "displayName": now_records[record],
                    "time": datetime.datetime.now(),
                })
        # 如果现在的记录不在数据库中,则插入
        for record in now_records:
            if record not in all_records:
                update_list.append({
                    "serverId": record.split("-")[0],
                    "personaId": record.split("-")[1],
                    "displayName": now_records[record],
                    "time": datetime.datetime.now(),
                })
        # 更新
        await orm.insert_or_update_batch(
            table=Bf1ServerOwner,
            data_list=update_list,
            conditions_list=[
                (Bf1ServerOwner.serverId == record["serverId"],
                 Bf1ServerOwner.personaId == record["personaId"])
                for record in update_list
            ]
        )
        # 删除
        await orm.delete_batch(
            table=Bf1ServerOwner,
            conditions_list=[
                (Bf1ServerOwner.serverId == record["serverId"], Bf1ServerOwner.personaId == record["personaId"]) for
                record in delete_list]
        )

    @staticmethod
    async def get_server_bookmark() -> list:
        """
        获取所有服务器的bookmark数
        :return: [{serverName: serverName, bookmark: bookmark}]
        """
        # 查询max(time) - 1s的时间
        time_temp = await orm.fetch_one(
            select(func.max(Bf1ServerPlayerCount.time))
        )
        time_temp = time_temp[0] - datetime.timedelta(seconds=1)
        if not time_temp:
            return []
        if result := await orm.fetch_all(
                select(Bf1ServerPlayerCount.serverId, Bf1ServerPlayerCount.serverBookmarkCount).where(
                    Bf1ServerPlayerCount.time >= time_temp
                )
        ):
            # 根据serverId查询serverName
            server_list = []
            for item in result:
                serverId = item[0]
                if server := await orm.fetch_one(
                        select(Bf1Server.serverName).where(
                            Bf1Server.serverId == serverId
                        )
                ):
                    server_list.append({
                        "serverName": server[0],
                        "bookmark": item[1]
                    })
            # 按bookmark降序排序
            server_list.sort(key=lambda x: x["bookmark"], reverse=True)
            return server_list
        else:
            return []

    # TODO:
    #   bf群组相关
    #   读:
    #   根据kook来获取对应绑定的群组
    #   根据对应guid获取服务器信息
    #   写:
    #   创建群组名和服务器信息

    @staticmethod
    async def get_bf1_group_by_kook(kook_group_id: int) -> Bf1Group:
        """根据kook群号获取对应绑定的bf1群组"""
        group_bind = await orm.fetch_one(
            select(Bf1GroupBind).where(Bf1GroupBind.kook_group_id == kook_group_id)
        )
        if group_bind:
            bf1_group = await orm.fetch_one(
                select(Bf1Group).where(Bf1Group.id == group_bind[0].bf1_group_id)
            )
            return bf1_group[0]
        return None

    @staticmethod
    async def get_bf1_server_by_guid(guid: str) -> Bf1Server:
        """根据guid获取服务器信息"""
        server = await orm.fetch_one(
            select(Bf1Server).where(Bf1Server.persistedGameId == guid)
        )
        if server:
            return server[0]
        return None

    @staticmethod
    async def create_kook_group_to_bf1_group(bf1_group_name: str) -> bool:
        """创建bf1群组"""
        try:
            bf1_group = await orm.fetch_one(
                select(Bf1Group).where(Bf1Group.group_name == bf1_group_name)
            )
            if bf1_group is None:
                data = {
                    "group_name": bf1_group_name
                }
                await orm.add(Bf1Group, data)
                return True
            else:
                logger.warning("group_name already exists")

            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    async def insert_or_update_bfgroup_server_admin(group_name: str, kookid: int, kooknickname: str,
                                                    level: int) -> bool:
        """"添加群组管理员或所有者"""
        data = {
            "group_name": group_name,
            "kookid": kookid,
            "kooknickname": kooknickname,
            "permission_level": level
        }
        await orm.add(Bf1GroupAdmin, data)
        return True

    @staticmethod
    async def delete_bfgroup_server_admin(group_name: str, kookid: int, kooknickname: str, level: int) -> bool:
        """"添加群组管理员或所有者"""
        condition = [Bf1GroupAdmin.group_name == group_name, Bf1GroupAdmin.kookid == kookid,
                     Bf1GroupAdmin.kooknickname == kooknickname]
        await orm.delete(Bf1GroupAdmin, condition)
        return True

    @staticmethod
    async def list_bfgroup_server_admin(group_name: str) -> list:
        """"列出群组管理员或所有者"""
        if adminlist := await orm.fetch_all(select(Bf1GroupAdmin.kooknickname, Bf1GroupAdmin.permission_level).where(
                Bf1GroupAdmin.group_name == group_name)):
            return [i for i in adminlist]
        else:
            return None

    @staticmethod
    async def get_user_permission_level(uid: int) -> int:
        """"获取玩家权限"""
        if level := await orm.fetch_one(select(Bf1GroupAdmin.permission_level).where(Bf1GroupAdmin.kookid == uid)):
            return level
        else:
            return [(2)]

    @staticmethod
    async def get_group_name_by_id(uid: int) -> list:
        """"列出玩家权限所在群组"""
        if g_list := await orm.fetch_all(select(Bf1GroupAdmin.group_name).where(Bf1GroupAdmin.kookid == uid)):
            return [i[0] for i in g_list]
        else:
            return []

    @staticmethod
    async def insert_or_update_bfgroup_server(bf1_group_name: str, severs_name: str, server_guid: str) -> bool:
        """添加或者修改bf1群组绑定的服务器信息"""
        try:
            bfgroup = await orm.fetch_one(select(Bf1Group.bind_guids).where(Bf1Group.group_name == bf1_group_name))
            logger.debug(bfgroup)
            if bfgroup[0] is not None:
                bfgroup[0][severs_name] = server_guid
                data = {
                    "group_name": bf1_group_name,
                    "bind_guids": bfgroup[0],
                }
                condition = [
                    Bf1Group.group_name == bf1_group_name,
                ]
                await orm.insert_or_update(Bf1Group, data, condition)
            else:
                data = {
                    "group_name": bf1_group_name,
                    "bind_guids": {severs_name: server_guid},
                }
                condition = [
                    Bf1Group.group_name == bf1_group_name,
                ]
                await orm.insert_or_update(Bf1Group, data, condition)
        except Exception as e:
            logger.exception(e)
            return False
        return True

    @staticmethod
    async def remove_bfgroup_server(bf1_group_name: str, severs_name: str) -> bool:
        try:
            bfgroup = await orm.fetch_one(select(Bf1Group.bind_guids).where(Bf1Group.group_name == bf1_group_name))
            if bfgroup[0] is not None:
                if severs_name in bfgroup[0]:
                    bfgroup[0].pop(severs_name, None)
                else:
                    logger.warning("删除的服务器不在该群组中")
                    return False
            else:
                logger.warning("删除的服务器群组为空")
                return False
            data = {
                "group_name": bf1_group_name,
                "bind_guids": bfgroup[0],
            }
            condition = [
                Bf1Group.group_name == bf1_group_name,
            ]
            await orm.insert_or_update(Bf1Group, data, condition)
        except Exception as e:
            logger.exception(e)
        return True

    @staticmethod
    async def list_bfgroup_server(bf1_group_name: str) -> list:
        """列出bf1群组绑定的服务器信息"""
        try:
            bfgroup = await orm.fetch_one(select(Bf1Group.bind_guids).where(Bf1Group.group_name == bf1_group_name))
            logger.debug(bfgroup)
            if bfgroup is None:
                return False
            if bfgroup[0] is not None:
                output = []
                for k, v in bfgroup[0].items():
                    server = await orm.fetch_one(
                        select(Bf1Server.serverName, Bf1Server.serverId, Bf1Server.gameId).where(
                            Bf1Server.persistedGameId == v)
                    )
                    output.append([server[0], server[1], server[2], v])

                return output
            else:
                logger.warning("群组服务器为空")
                return False
        except Exception as e:
            logger.exception(e)
            return False

    @staticmethod
    async def get_bfgroup_server_info_by_server_server_name(server_name: str) -> list:
        """查找bf1群组绑定的服务器信息"""
        try:
            bfgroup = await orm.fetch_one(select(Bf1Group.bind_guids).where(Bf1Group.group_name == server_name[0:-1]))
            logger.debug(bfgroup)
            if bfgroup is None:
                logger.info(f"{server_name[0:-2]}不存在")
                return False
            if bfgroup[0] is not None:
                if server_name not in bfgroup[0]:
                    return False
                output = []
                guid = bfgroup[0][server_name]
                server = await orm.fetch_one(
                    select(Bf1Server.serverId, Bf1Server.gameId).where(Bf1Server.persistedGameId == guid)
                )
                output.append([server[0], server[1], guid])
                return output
            else:
                logger.warning(f"{server_name[0:-2]}群组服务器为空")
                return False
        except Exception as e:
            logger.exception(e)
            return False

    @staticmethod
    async def add_rsp_log(author_id: str, nickname: str, server_id: str, server_guid: str, server_gameid: str,
                          player_pid: str, player_name: str, type: str, content: str, time: str) -> bool:
        """用于添加服管日志记录
        Args:
            author_id (str): 操作者kookid
            nickname (str): 操作者昵称
            server_id (str): 服务器id
            server_guid (str): 服务器guid
            server_gameid (str): 服务器gameid
            player_pid (str): 被操作玩家id
            type (str): 操作类型
            content (str): 完整日志
            time (str): 操作时间
        Returns:
            bool: 是否记录成功
        """
        try:
            data = {
                "kookid": author_id,
                "kooknickname": nickname,
                "serverId": server_id,
                "persistedGameId": server_guid,
                "gameId": server_gameid,
                "persona_id": player_pid,
                "display_name": player_name,
                "log_type": type,
                "log_content": content,
                "log_time": time,
            }
            await orm.add(Bf1ManagerLog, data)
        except  Exception as e:
            logger.exception(e)
        return True

    @staticmethod
    async def get_group_bindList() -> list:
        bfgroupac = await orm.fetch_all(select(Bf1Account.display_name))
        output = []
        for i in bfgroupac:
            output.append(i[0].upper())
        return output

    # TODO
    #   btr对局缓存
    #   读:
    #   根据玩家pid获取对应的btr对局信息
    #   写:
    #   写入btr对局信息
    @staticmethod
    async def get_btr_match_by_displayName(display_name: str) -> Union[list, None]:
        """根据pid获取对应的btr对局信息"""
        # 根据时间获取该display_name最新的10条记录
        if match := await orm.fetch_all(
                select(
                    Bf1MatchCache.match_id, Bf1MatchCache.server_name,
                    Bf1MatchCache.map_name, Bf1MatchCache.mode_name,
                    Bf1MatchCache.time, Bf1MatchCache.team_name,
                    Bf1MatchCache.team_win, Bf1MatchCache.persona_id,
                    Bf1MatchCache.display_name, Bf1MatchCache.kills,
                    Bf1MatchCache.deaths, Bf1MatchCache.kd, Bf1MatchCache.kpm,
                    Bf1MatchCache.score, Bf1MatchCache.spm,
                    Bf1MatchCache.accuracy, Bf1MatchCache.headshots,
                    Bf1MatchCache.time_played
                ).where(Bf1MatchCache.display_name == display_name).order_by(Bf1MatchCache.time.desc()).limit(5)
        ):
            result = []
            for match_item in match:
                temp = {"match_id": match_item[0], "server_name": match_item[1], "map_name": match_item[2],
                        "mode_name": match_item[3], "time": match_item[4], "team_name": match_item[5],
                        "team_win": match_item[6], "persona_id": match_item[7], "display_name": match_item[8],
                        "kills": match_item[9], "deaths": match_item[10], "kd": match_item[11], "kpm": match_item[12],
                        "score": match_item[13], "spm": match_item[14], "accuracy": match_item[15],
                        "headshots": match_item[16], "time_played": match_item[17]}
                result.append(temp)
            return result
        return None

    @staticmethod
    async def update_btr_match_cache(
            match_id: int, server_name: str, map_name: str, mode_name: str, time: datetime.datetime,
            team_name: str, team_win: bool, display_name: str, kills: int,
            deaths: int, kd: float, kpm: float, score: int, spm: float, accuracy: str,
            headshots: str, time_played: int, persona_id: int = 0,
    ) -> bool:
        await orm.insert_or_ignore(
            table=Bf1MatchCache,
            data={
                "id": str(uuid.uuid4()),  # 暂代
                "match_id": match_id,
                "server_name": server_name,
                "map_name": map_name,
                "mode_name": mode_name,
                "time": time,
                "team_name": team_name,
                "team_win": team_win,
                "persona_id": persona_id,
                "display_name": display_name,
                "kills": kills,
                "deaths": deaths,
                "kd": kd,
                "kpm": kpm,
                "score": score,
                "spm": spm,
                "accuracy": accuracy,
                "headshots": headshots,
                "time_played": time_played
            },
            condition=[
                Bf1MatchCache.match_id == match_id,
                Bf1MatchCache.display_name == display_name
            ]
        )

    @staticmethod
    async def get_bf1log_by_player_name(player_name: str) -> list:
        if log := await orm.fetch_all(
                select(Bf1ManagerLog.kooknickname, Bf1ManagerLog.display_name, Bf1ManagerLog.log_type,
                       Bf1ManagerLog.log_time, Bf1ManagerLog.log_content).where(
                    Bf1ManagerLog.display_name == player_name)):
            return [i for i in log]
        else:
            return None

    @staticmethod
    async def insert_bf1import(name: str, pid: str) -> bool:
        try:
            if temp := await orm.fetch_one(
                    select(Bf1Import.pid_list).where(
                        Bf1Import.name == name)):
                pidlist = json.loads(temp[0], strict=False)
                pidlist = list(pidlist)
            else:
                pidlist = []
            pidlist.append(pid)
            pidset = set(pidlist)
            pidlist = list(pidset)
            if temp := await orm.insert_or_update(Bf1Import, {"name": name, "pid_list": f'{pidlist}'},
                                                  [Bf1Import.name == name]):
                return True
        except Exception as e:
            logger.exception(e)

    @staticmethod
    async def list_bf1import(name: str) -> list:
        if temp := await orm.fetch_one(
                select(Bf1Import.pid_list).where(
                    Bf1Import.name == name)):
            pidlist = json.loads(temp[0], strict=False)
            pidlist = list(pidlist)
            return pidlist
        else:
            return None


BF1DB = bf1_db()

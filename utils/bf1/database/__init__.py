import datetime
from typing import Union, List, Tuple, Dict, Any

from loguru import logger
from sqlalchemy import select, func

from utils.bf1.database.tables import orm, Bf1Account,Permission,Banweapon
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
    #  权限表
    #  读：
    #  根据kookid获取权限等级
    #  写：
    #  更新用户等级
    @staticmethod
    async def get_level_by_kookid(kook_id: int) -> dict:
        """
        根据kookid获取权限等级
        :param kook_id:kook uid 
        :return: 有结果时,返回dict,无结果时返回None
        """
        if account := await orm.fetch_one(
                select(
                    Permission.permission_level
                ).where(
                    Permission.kook_id == kook_id
                )
        ):
            return {
                "permission_level": account[0],
            }
        else:
            return None
   
#async def update_level_by_kookid(kook_id: int,level:int) -> dict:
    # TODO:
    #  武器禁用表
    #  读：
    #  读取武器禁用表
    #  写：
    #  更新武器禁用表
    @staticmethod
    async def get_weapon_ban(weapon_ban_name:str) -> List:
        try:
            bfgroup = await orm.fetch_one(select(Banweapon.ban_weapon_list).where(Banweapon.ban_name == weapon_ban_name))
            return bfgroup[0]['0']
        except Exception as e:
            logger.exception(e)
            return False
    @staticmethod
    async def update_weapon_ban(weapon_ban_name:str,weapon_ban_list: list) -> bool:
        try:
            bfgroup = await orm.fetch_one(select(Banweapon.ban_weapon_list).where(Banweapon.ban_name == weapon_ban_name))
            logger.debug(bfgroup)
            if bfgroup is not None:
                set1 = set(bfgroup[0]['0'])
                set2 = set(weapon_ban_list)
                merged_set = set1.union(set2)
                merged_list = list(merged_set)
                bfgroup[0]['0'] = merged_list
                data = {
                    "ban_name": weapon_ban_name,
                    "ban_weapon_list": bfgroup[0],
                }
                condition = [
                    Banweapon.ban_name == weapon_ban_name,
                ]
                await orm.insert_or_update(Banweapon, data, condition)
            else:
                data = {
                    "ban_name": weapon_ban_name,
                    "ban_weapon_list": {0:weapon_ban_list},
                }
                condition = [
                    Banweapon.ban_name == weapon_ban_name,
                ]
                await orm.insert_or_update(Banweapon, data, condition)
        except Exception as e:
            logger.exception(e)
            return False
        return True
    @staticmethod
    async def del_weapon_ban(weapon_ban_name:str,weapon: str) -> bool:
        try:
            bfgroup = await orm.fetch_one(select(Banweapon.ban_weapon_list).where(Banweapon.ban_name == weapon_ban_name))
            logger.debug(bfgroup)
            if bfgroup is not None:
                if weapon in bfgroup[0]['0']:
                    del bfgroup[0]['0'][bfgroup[0]['0'].index(weapon)]
                else:
                    return False
                data = {
                    "ban_name": weapon_ban_name,
                    "ban_weapon_list": bfgroup[0],
                }
                condition = [
                    Banweapon.ban_name == weapon_ban_name,
                ]
                await orm.insert_or_update(Banweapon, data, condition)
            else:
                return False
        except Exception as e:
            logger.exception(e)
            return False
        return True

BF1DB = bf1_db()

import datetime
from typing import Union, List, Tuple, Dict, Any

from loguru import logger
from sqlalchemy import select, func
from utils.kook.database.tables import orm,ChatLog

class kook_db:
    # TODO:
    #  kook日志相关
    #  读：
    #  根据uid（kookid）获取使用机器人情况
    #  根据nickname 获取使用机器人情况
    #  写：
    #  根据机器人命令被调用时写入日志
    @staticmethod
    async def get_log_by_uid(uid: int) -> list:
        """
        根据uid获取玩家信息
        :param uid: kook账号id（可通过处理@信息获得）
        :return: 有结果时,返回str,无结果时返回None
        """
        if log := await orm.fetch_all(
                select(
                    ChatLog.user_id,  ChatLog.nickname, ChatLog.server_id,
                    ChatLog.channel_id, ChatLog.timestamp, ChatLog.message
                ).where(
                    ChatLog.user_id == uid
                )
        ):
            return [i for i in log]
    @staticmethod
    async def add_log(
            user_id: int, nickname: str, channel_id: int, timestamp:datetime,server_id:int,message:str
    ) -> bool:
        await orm.add(
            table=ChatLog,
            data={
                "user_id": user_id,
                "nickname": nickname,
                "channel_id": channel_id,
                "timestamp": timestamp,
                "server_id": server_id,
                "message": message
            },
        )           
KOOKDB = kook_db()
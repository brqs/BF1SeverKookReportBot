from utils.kook.database import KOOKDB
from utils.bf1.database import BF1DB
from functools import wraps
from loguru import logger
from khl import PublicMessage
import datetime

def msg_log():
    def decorator(fn):
        @wraps(fn)
        async def rev_logger(msg: PublicMessage, *args, **kwargs):
            await KOOKDB.add_log(msg.author.id,msg.author.nickname,msg.channel.name,datetime.datetime.now(),msg.guild.master_id,msg.content.strip().replace('\n', '\\n'))
            logger.info(
                f"收到来自 服务器[{msg.guild.master_id}] 频道{msg.channel.name} "
                f"用户{msg.author.nickname}[{msg.author.id}(状态{msg.author.status})] 的消息: " + msg.content.strip().replace(
                    '\n', '\\n')
            )
            return await fn(msg, *args, **kwargs)
        return rev_logger
    return decorator
def permission_required(permission_level):
    def decorator(fn):
        try:
            @wraps(fn)
            async def permission(msg: PublicMessage, *args, **kwargs):
            # 检查用户权限
                user_permission = await BF1DB.get_user_permission_level(msg.author_id)
                if user_permission[0]>=16:
                    return await fn(msg, *args, **kwargs)
                if permission_level==1:
                    return await fn(msg, *args, **kwargs)
                if user_permission[0] >= permission_level:
                    # 检查群组名称是否与参数匹配
                    group_name_list = await BF1DB.get_group_name_by_id(msg.author_id)
                    if not (len(args) >= 1 and (args[0] in group_name_list or args[0][0:-1] in group_name_list)):
                        return await msg.reply("您只能操作自己所在的群组。")
                    return await fn(msg, *args, **kwargs)
                else:
                    return await msg.reply(f"权限不足,该命令需要的权限为{permission_level}，您的权限为{user_permission[0]}")
            return permission
        except Exception as e:
            logger.exception(e)
    return decorator
from khl import Bot, Message
from loguru import logger
from utils.bf1.default_account import BF1DA
from utils.bf1.gateway_api import api_instance
import yaml
#从配置文件读取
with open('./config/config.yaml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)
    token = data['botinfo'].get('token')[0]
# init Bot
bot = Bot(token)

#检查默认账号
@bot.on_startup
async def check_default_account(self):
    logger.debug("正在检查默认账号信息")
    # 检查默认账号信息
    default_account_info = await BF1DA.read_default_account()
    if not default_account_info["pid"]:
       logger.warning("BF1默认查询账号信息不完整，请使用 '-设置默认账号 pid remid=xxx,sid=xxx' 命令设置默认账号信息")
    # 登录默认账号
    await BF1DA.get_api_instance()
    # 更新默认账号信息
    if account_info := await BF1DA.update_player_info():
        logger.debug("默认账号信息检查完毕")
        # 给Master发送提示
        return  logger.warning(
                f"BF1默认查询账号信息已更新，当前默认账号信息为：\n"+
                f"display_name: {account_info['display_name']}\n"+
                f"pid: {account_info['pid']}\n"+
                f"session: {account_info['session']}"
            )
    else:
        logger.warning("默认账号信息更新失败")
        # 给Master发送提示
        return  logger.warning("BF1更新默认查询账号失败!")
# 设置默认账号信息
@bot.command(name='设置默认账号',aliases=['设置默认账号', 'sda'],prefixes=['/','\\','-','、','.','。'])
async def set_default_account(
        msg:Message,
        account_pid: str,
        remid: str,
        sid: str
):
    # 如果pid不是数字,则返回错误信息
    if not account_pid.isdigit():
        return await msg.reply("pid必须为数字")
    else:
        account_pid = int(account_pid)
    # 登录默认账号
    try:
        await msg.reply(f"正在登录默认账号{account_pid}")
        # 数据库写入默认账号信息
        await BF1DA.write_default_account(
            pid=account_pid,
            remid=remid,
            sid=sid
        )
        BF1DA.account_instance = api_instance.get_api_instance(account_pid)
        session = await (await BF1DA.get_api_instance()).login(remid=remid, sid=sid)
    except Exception as e:
        logger.error(e)
        return await msg.reply(f"登录默认账号{account_pid}失败，请检查remid和sid是否正确")
    if not isinstance(session, str):
        # 登录失败,返回错误信息
        return await msg.reply(f"登录默认账号{account_pid}失败，错误信息: {session}")
    logger.success(f"登录默认账号{account_pid}成功")
    # 登录成功,返回账号信息和session
    player_info = await (await BF1DA.get_api_instance()).getPersonasByIds(account_pid)
    # 如果pid不存在,则返回错误信息
    if isinstance(player_info, str) or not player_info.get("result"):
        return await msg.reply(
                f"登录默认账号{account_pid}成功,但是pid不存在,请检查pid是否正确!!!\n请在 utils/bf1/default_account.json 中修改默认账号的pid信息以保证账号的正常查询!"
            )
    displayName = f"{player_info['result'][str(account_pid)]['displayName']}"
    pid = f"{player_info['result'][str(account_pid)]['personaId']}"
    uid = f"{player_info['result'][str(account_pid)]['nucleusId']}"
    return await msg.reply(
            f"登录默认账号{account_pid}成功!\n"
            +f"账号信息如下:\n"
            +f"displayName: {displayName}\n"
            +f"pid: {pid}\n"
            +f"uid: {uid}\n"
            +f"remid: {remid}\n"
            +f"sid: {sid}\n"
            +f"session: {session}"
        )
 
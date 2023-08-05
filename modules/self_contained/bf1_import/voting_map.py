from .utils import get_gid
from utils.bf1.database import BF1DB
from utils.bf1.default_account import BF1DA
async def get_map_list():
    server_gid = get_gid()
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
            f"{i}#{item['modePrettyName']}-{item['mapPrettyName']}●\n".replace('流血', '流\u200b血')
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
            else f"{i}#{item['modePrettyName']}-{item['mapPrettyName']}\n".replace('流血', '流\u200b血')
        )
        choices.append(str(i))
        i += 1
    return map_list


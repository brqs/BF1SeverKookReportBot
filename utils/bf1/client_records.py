from loguru import logger
import time
import socket
import json
import time
import threading
from queue import Queue
import socket
from client_utils import Clientutils
import chardet
# 检测文件编码
with open('./utils/bf1/weapon_dict.json', 'rb') as file:
    raw_data = file.read()
    encoding = chardet.detect(raw_data)['encoding']

# 读取JSON文件（使用检测到的编码）
with open('./utils/bf1/weapon_dict.json', 'r', encoding=encoding) as file:
    weapon_data = json.load(file)
class GameKillRecord:
    def __init__(self):
        self.server_ip = '127.0.0.1'
        self.server_port = 52002
        # 创建 UDP 客户端
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 绑定客户端到指定的 IP 地址和端口
        self.client_socket.bind((self.server_ip, self.server_port))
        self.kill_record_queue = Queue()
        self.servername="ddf1"
        self.get_server_info()
    def kill_record_worker(self):
        while True:
            data, addr = self.client_socket.recvfrom(1024)
            kill = data.decode('utf-8')
            try:
                if kill.startswith('{'):
                    kill_data = json.loads(kill)
                    send_message=f"`{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))}`服务器{self.servername}玩家`{kill_data['killer']['name']}`使用{weapon_data[kill_data['killedBy']]}击杀`{kill_data['victim']['name']}`\n"
                    self.kill_record_queue.put(send_message)
            except Exception as e:
                logger.error(e)
    def start(self):
        send_thread = threading.Thread(target=self.kill_record_worker)
        send_thread.daemon = True
        send_thread.start()
    def get_server_info(self):
        try:
            if Clientutils.get_server_Ingame():
                info=Clientutils.get_server_data("server")
                self.servername=info['name'][:10]
                self.player=Clientutils.get_server_data("player")['name']
        except Exception as e:
            logger.error("请检查服务器是否开启")    
if __name__ == '__main__':
  
    gk=GameKillRecord()
    gk.start()
    
    while True:
        print(gk.kill_record_queue.get())


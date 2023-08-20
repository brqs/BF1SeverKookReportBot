from zhconv import convert  
import socket
import threading
from queue import Queue
import json
import time
from loguru import logger
from .client_utils import Clientutils
import json
class GameChat:
    def __init__(self):
        # 游戏聊天服务器地址和端口
        self.GAME_CHAT_ADDRESS = '127.0.0.1'
        self.GAME_CHAT_PORT = 51001
        # 我们应用程序的地址和端口
        self.APP_ADDRESS = '127.0.0.1'
        self.APP_PORT = 52001
        # 发送消息的频率限制（秒）
        self.SEND_FREQ_LIMIT = 1
        # 初始化 UDP socket 用于接收游戏聊天消息
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket.bind((self.APP_ADDRESS, self.APP_PORT))
        # 初始化 UDP socket 用于发送游戏聊天消息
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 初始化变量以跟踪发送频率
        self.last_send_time = 0
        self.lock = threading.Lock()
        # 初始化 zhconv 转换器，用于繁简中文转换
        self.converter = convert
        self.message_queue = Queue()
        self.message_set={'存储聊天信息的集合'}
        self.sended_message_set={'存储聊天信息的集合'}
        self.servername="ddf1"
        self.mapdict={}
        self.map=[]
        self.get_server_info()
    def send_chat_worker(self):
        """
        用于从队列中取出消息并发送到游戏聊天服务器的函数。
        在单独的线程中运行。
        """
        while True:
            message = self.message_queue.get()
            # 将消息转换为繁体中文
            if type(message) ==str:
                text = self.converter(message, 'zh-tw')
                # 将消息编码为 UTF-8 字节
                time1=time.time()
                message = f"#Chat.Send#{text}".encode('utf-8')
                try:
                    #logger.info(f'发送{text}中')
                    self.send_socket.sendto(message, (self.GAME_CHAT_ADDRESS, self.GAME_CHAT_PORT))
                    time.sleep(1)
                    # 发送完毕后移除消息
                except Exception as e:
                    logger.error(f"发送游戏聊天消息时出错：{e}")
                finally:
                    self.message_queue.task_done()
                    time2=time.time()
                    #logger.info(f'发送完成，剩余消息队列长度为{self.message_queue.qsize()}，耗时{time2-time1}')
    def start(self):
        self.get_server_info()
        send_thread = threading.Thread(target=self.send_chat_worker)
        send_thread.daemon = True
        send_thread.start()
        receive_thread = threading.Thread(target=self.receive_chat)
        receive_thread.daemon = True
        receive_thread.start()
    def receive_chat(self):
        """
        用于在后台接收游戏聊天消息的函数。
        在单独的线程中运行。
        """
        while True:
            data, addr = self.recv_socket.recvfrom(1024)
            message = data.decode('utf-8')
            if message.startswith('{'):
                message_data = json.loads(message)
                send_message=f"`{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))}`服务器{self.servername}玩家`{message_data['name']}`说`{message_data['content']}`\n"
                self.message_set.add(send_message)
                try:
                    if message_data['content'].replace('\x00', '') in ["1","2","3","4","5"]:
                        self.mapdict[message_data['name']]=message_data['content'].replace('\x00', '')
                except Exception as e:
                    logger.exception(e)
    def get_server_info(self):
        try:
            if Clientutils.get_server_Ingame():
                info=Clientutils.get_server_data("server")
                self.servername=info['name'][:10]
                self.player=Clientutils.get_server_data("player")['name']
        except Exception as e:
            logger.error("请检查服务器是否开启")
    def get_send_kook_message(self):
        if self.message_set==self.sended_message_set:
            return False
        self.send_message_set=self.message_set-self.sended_message_set
        for e in self.message_set:
            self.sended_message_set.add(e)
        sorted_messages = sorted(self.send_message_set, key=self.sort_by_time)
        send_message="\n".join(s for s in sorted_messages if self.player not in s)
        self.message_set={'存储聊天信息的集合'}
        self.sended_message_set={'存储聊天信息的集合'}
        return send_message
    def sort_by_time(self,message):
        time_str = message.split('`')[1]  # 解析出时间字符串
        timestamp = time.mktime(time.strptime(time_str, '%Y/%m/%d %H:%M:%S'))  # 转换为时间戳
        return timestamp          
gc=GameChat()
gc.start()

   
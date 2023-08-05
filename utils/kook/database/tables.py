from sqlalchemy import Column, Integer, BIGINT, String, DateTime
from core.orm import orm
# kook log表
class ChatLog(orm.Base):
    __tablename__ = 'chat_logs'
    """log信息"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    server_id = Column(BIGINT, nullable=False)
    channel_id = Column(BIGINT, nullable=False)
    user_id = Column(BIGINT, nullable=False)
    nickname=Column(String, nullable=False)
    message = Column(String, nullable=False)

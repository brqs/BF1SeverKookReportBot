from sqlalchemy import Column, Integer, BIGINT, String, ARRAY, DateTime, ForeignKey, JSON, Boolean

from core.orm import orm
# bf1账号表
class Bf1Account(orm.Base):
    """bf1账号信息"""

    __tablename__ = "bf1_account"

    id = Column(Integer, primary_key=True)
    # 固定
    persona_id = Column(BIGINT)
    # 一般固定
    user_id = Column(BIGINT)
    # 变化
    name = Column(String)
    # 变化
    display_name = Column(String)

    remid = Column(String)
    sid = Column(String)
    session = Column(String)
class Permission(orm.Base):
    """权限表"""
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True)
    # 固定
    kook_id = Column(BIGINT)
    # 一般固定
    permission_level = Column(Integer)
    # 变化
class Banweapon(orm.Base):
    """禁用武器表"""
    __tablename__ = "banweapon"
    id = Column(Integer, primary_key=True)
    ban_name = Column(String)
    ban_weapon_list =  Column(JSON)
class KillRecord(orm.Base):
    """击杀记录表"""
    __tablename__ = "killrecord"
    id = Column(Integer, primary_key=True)
    time=Column(DateTime)
    killedBy=Column(String)
    isHeadshot=Column(String)
    killedType=Column(String)
    killerPid=Column(String)
    killerClan=Column(String)
    killerName=Column(String)
    killerTeam=Column(String)
    victimPid=Column(String)
    victimClan=Column(String)
    victimName=Column(String)
    victimTeam=Column(String)
    serverName=Column(String)
    serverGameId=Column(String)
    serverMode=Column(String)
    serverMap=Column(String)
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

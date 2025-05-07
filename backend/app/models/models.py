from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Text, DateTime, ForeignKey, func, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# class User(Base):
#     __tablename__ = "users"
#     id = Column(String, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     name = Column(String)
#     picture = Column(String)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     last_login_at = Column(DateTime(timezone=True))

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    picture = Column(String)
    role_level = Column(Integer, nullable=False, default=1)  # <-- NEW!
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True))


class UserCredit(Base):
    __tablename__ = "user_credits"
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    credits_balance = Column(BigInteger, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CreditPurchase(Base):
    __tablename__ = "credit_purchases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    credits_added = Column(Integer, nullable=False)
    payment_provider = Column(String)
    payment_reference = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Feature(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_free = Column(Boolean, default=False)
    credit_cost = Column(Integer, default=0)


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    activity_type = Column(String, nullable=False)
    feature_id = Column(Integer, ForeignKey("features.id", ondelete="SET NULL"), nullable=True)
    details = Column(Text)
    ip_address = Column(String)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CreditUsage(Base):
    __tablename__ = "credit_usage"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    feature_id = Column(Integer, ForeignKey("features.id", ondelete="SET NULL"))
    credits_used = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())





class UserRole(Base):
    __tablename__ = "user_roles"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(Text, unique=True, nullable=False)
    role_level = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('role_level > 0', name='check_role_level_positive'),
    )
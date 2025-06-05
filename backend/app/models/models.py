from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Text, DateTime, ForeignKey, func, UniqueConstraint, CheckConstraint,JSON
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime, timezone

Base = declarative_base()


class PDF(Base):
    __tablename__ = 'pdf'
    __table_args__ = {'schema': 'vector'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pdf_name = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    uploaded_by_user_id = Column(String, index=True)
    total_pages = Column(Integer)
    uploaded_on_utc = Column(DateTime)
    
class PDFChunk(Base):
    __tablename__ = 'pdf_chunks'
    __table_args__ = {'schema': 'vector'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk = Column(String, nullable=False)
    pdf_id = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    chunk_number = Column(Integer, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    uploaded_by_user_id = Column(String, index=True)
    created_on_utc = Column(DateTime)
    
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
    tts_history = relationship("TTSHistory", back_populates="user")
    asr_history = relationship("ASRHistory", back_populates="user")
    api_key = Column(String, unique=True, index=True, nullable=True)  



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


# class UserActivityLog(Base):
#     __tablename__ = "user_activity_logs"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
#     activity_type = Column(String, nullable=False)
#     feature_id = Column(Integer, ForeignKey("features.id", ondelete="SET NULL"), nullable=True)
#     details = Column(Text)
#     ip_address = Column(String)
#     user_agent = Column(Text)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    activity_type = Column(String, nullable=False)
    feature_id = Column(Integer, ForeignKey("features.id", ondelete="SET NULL"), nullable=True)
    details = Column(Text)
    ip_address = Column(String)
    user_agent = Column(Text)
    ssid = Column(String(255))  # safe for encoded cookie session
    logged_in = Column(DateTime(timezone=True))  # NEW: login time
    logged_out = Column(DateTime(timezone=True))  # NEW: logout time
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


class TTSHistory(Base):
    __tablename__ = "tts_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    text = Column(String, nullable=False)
    language = Column(String, nullable=False)
    audio_file_path = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="tts_history")



class ASRHistory(Base):
    __tablename__ = "asr_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    language = Column(String)
    transcript = Column(String)
    audio_path = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="asr_history")



class UserDetails(Base):
    __tablename__ = "user_details"

    id = Column(Integer, primary_key=True, index=True)
    caller_id = Column(String, index=True)
    name = Column(String, index=True)
    phone_number = Column(String, index=True)
    call_type = Column(JSON)  # OPTIONAL: if you want a minimal copy in Postgres too
    tts_folder_location = Column(String, index=True)
    status = Column(String, index=True)
    assigned_container = Column(String, index=True)
    scheduled_for_utc = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    modified_on_utc = Column(DateTime, default=lambda: datetime.now(timezone.utc))
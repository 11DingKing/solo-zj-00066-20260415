from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    date_signed_up = Column(DateTime(), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    operations = relationship('OperationLog', back_populates='user', lazy='dynamic')


class Signups(Base):
    """
    Example Signups table (for backward compatibility)
    """
    __tablename__ = 'signups'
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    email = Column(String(256), unique=True)
    date_signed_up = Column(DateTime())


class OperationLog(Base):
    __tablename__ = 'operation_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(128), nullable=False)
    details = Column(String(512))
    timestamp = Column(DateTime(), nullable=False)

    user = relationship('User', back_populates='operations')

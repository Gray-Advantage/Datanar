from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Integer, DateTime
from database.database_session import SqlAlchemyBase
from sqlalchemy.dialects.mysql import TINYINT
from flask_login import UserMixin
from datetime import datetime


class User(SqlAlchemyBase, UserMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=True, unique=True, index=True)
    date_of_creation = Column(DateTime, default=datetime.now)

    login = Column(String(255), nullable=True, unique=True, index=True)
    _hashed_password = Column(String(102), nullable=True)
    email = Column(String(255), unique=True, default=None)
    state = Column(TINYINT(unsigned=True), default=0)

    @property
    def password(self) -> str:
        return self._hashed_password

    @password.setter
    def password(self, password) -> None:
        self._hashed_password = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self._hashed_password, password)

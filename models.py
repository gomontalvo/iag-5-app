from sqlalchemy.orm import relationship
from db import db
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from datetime import datetime


class User(db.Model):
   __tablename__ = "users"

   id = Column(Integer, primary_key=True, autoincrement=True)
   created_at = Column(DateTime, default=datetime.utcnow)
   email = Column(String, nullable=False, unique=True)

   messages = relationship("Message", back_populates="user")
   preferencias= relationship("Preferencias", back_populates="user")


class Message(db.Model):
   __tablename__ = "messages"
   
   id = Column(Integer, primary_key=True, autoincrement=True)
   created_at = Column(DateTime, default=datetime.utcnow)
   content = Column(Text, nullable=False)
   author = Column(String, nullable=False)  # 'user' or 'assistant'
   user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
   user = relationship("User", back_populates="messages")

class Preferencias(db.Model):
   __tablename__ = "preferencias"
   #Id autoincremental
   id = Column(Integer, primary_key=True, autoincrement=True)
   #Texto de la preferencia, ejemplo: "Terror" (Genero pelicula), "Pesadilla 3" (Nombre de pelicula)
   preferencia = Column(Text, nullable=False)
   #String de la preferencia, ejemplo: "Genero", "Titulo"
   categoria = Column(String, nullable=False)  # 'user' or 'assistant'
   #ID (fk) del usuario,, tabla User
   user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
   user = relationship("User", back_populates="preferencias")

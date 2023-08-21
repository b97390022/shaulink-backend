
from __future__ import annotations

import datetime
from typing import List, Union
from sqlalchemy import func
from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "item"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    type: Mapped[int] = mapped_column(Integer)
    password: Mapped[str] = mapped_column(nullable=True)
    og_title: Mapped[str] = mapped_column(nullable=True)
    og_url: Mapped[str] = mapped_column(nullable=True)
    og_image: Mapped[str] = mapped_column(nullable=True)
    og_description: Mapped[str] = mapped_column(nullable=True)
    create_time: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    expired: Mapped[bool] = mapped_column(Boolean, default=False)
    url: Mapped[List[URL]] = relationship("URL", back_populates="item", cascade="all, delete-orphan")
    image: Mapped[List[Image]] = relationship("Image", back_populates="item", cascade="all, delete-orphan")
    video: Mapped[List[Video]] = relationship("Video", back_populates="item", cascade="all, delete-orphan")

class URL(Base):
    __tablename__ = "url"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement="auto")
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id", ondelete="CASCADE"))
    data: Mapped[str]
    item: Mapped[Item] = relationship("Item", back_populates="url")

class Image(Base):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement="auto")
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id", ondelete="CASCADE"))
    data: Mapped[str]
    media_type: Mapped[str]
    item: Mapped[Item] = relationship("Item", back_populates="image")

class Video(Base):
    __tablename__ = "video"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id", ondelete="CASCADE"))
    data: Mapped[str]
    media_type: Mapped[str]
    item: Mapped[Item] = relationship("Item", back_populates="video")
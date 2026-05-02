from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(2048))
    source: Mapped[str] = mapped_column(String(64))
    url: Mapped[str] = mapped_column(String(4096))
    score: Mapped[int] = mapped_column(Integer, default=0)
    category: Mapped[str] = mapped_column(String(128))
    crawled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class HookPattern(Base):
    __tablename__ = "hook_patterns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pattern: Mapped[str] = mapped_column(String(512), unique=True)
    template: Mapped[str] = mapped_column(Text)
    example: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(64))
    strength: Mapped[str] = mapped_column(String(32))
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    generated_posts: Mapped[list["GeneratedPost"]] = relationship(
        "GeneratedPost",
        back_populates="hook_pattern",
        cascade="all, delete-orphan",
    )


class GeneratedPost(Base):
    __tablename__ = "generated_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hook_pattern_id: Mapped[int] = mapped_column(
        ForeignKey("hook_patterns.id", ondelete="CASCADE")
    )
    topic: Mapped[str] = mapped_column(String(512))
    platform: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    hook_pattern: Mapped["HookPattern"] = relationship(
        "HookPattern", back_populates="generated_posts"
    )


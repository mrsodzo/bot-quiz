from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class QuizResult(Base):
    __tablename__ = "quiz_results"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int]
    username: Mapped[str | None]
    answers: Mapped[str] = mapped_column(Text)
    tariff: Mapped[str]
    price: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str]


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quiz_result_id: Mapped[int]
    name: Mapped[str]
    phone: Mapped[str]
    created_at: Mapped[str] = mapped_column(Text)

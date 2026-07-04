import json
import os
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import DB_PATH
from src.models import Base, Contact, QuizResult

engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}", echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    data_dir = os.path.dirname(DB_PATH)
    if data_dir:
        os.makedirs(data_dir, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_demo_data()


async def seed_demo_data():
    async with async_session() as session:
        existing = (await session.scalars(select(QuizResult))).first()
        if existing:
            return
        demo = QuizResult(
            user_id=999,
            username="demo",
            answers=json.dumps(
                {
                    "frequency": "1-2 раза в неделю",
                    "goal": "Похудение",
                    "preference": "Самостоятельно",
                    "experience": "Новичок",
                },
                ensure_ascii=False,
            ),
            tariff="Старт",
            price="1 900 ₽/мес",
            description="Базовый абонемент + вводная консультация",
            created_at=datetime.utcnow().isoformat(),
        )
        session.add(demo)
        await session.commit()


async def save_quiz_result(
    user_id: int, username: str | None, answers: dict, tariff: str, price: str, description: str
) -> int:
    async with async_session() as session:
        result = QuizResult(
            user_id=user_id,
            username=username,
            answers=json.dumps(answers, ensure_ascii=False),
            tariff=tariff,
            price=price,
            description=description,
            created_at=datetime.utcnow().isoformat(),
        )
        session.add(result)
        await session.commit()
        await session.refresh(result)
        return result.id


async def save_contact(quiz_result_id: int, name: str, phone: str):
    async with async_session() as session:
        contact = Contact(
            quiz_result_id=quiz_result_id,
            name=name,
            phone=phone,
            created_at=datetime.utcnow().isoformat(),
        )
        session.add(contact)
        await session.commit()
        await session.refresh(contact)


async def get_quiz_result_with_contact(result_id: int) -> dict:
    async with async_session() as session:
        result = await session.get(QuizResult, result_id)
        if not result:
            return {}
        contact = (
            await session.scalars(select(Contact).where(Contact.quiz_result_id == result_id))
        ).first()
        return {
            "id": result.id,
            "user_id": result.user_id,
            "username": result.username,
            "answers": result.answers,
            "tariff": result.tariff,
            "price": result.price,
            "description": result.description,
            "created_at": result.created_at,
            "contact": {
                "id": contact.id,
                "quiz_result_id": contact.quiz_result_id,
                "name": contact.name,
                "phone": contact.phone,
                "created_at": contact.created_at,
            }
            if contact
            else None,
        }

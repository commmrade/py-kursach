from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models import Formula
from schemas import FormulaCreate
from sqlalchemy import select

async def create_formula(db: AsyncSession, formula: FormulaCreate, user_id: int):
    stmt = insert(Formula).values(**formula.dict(), user_id=user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.inserted_primary_key[0]

async def get_formulas(db: AsyncSession, user_id: int):
    result = await db.execute(select(Formula).filter(Formula.user_id == user_id))
    return result.scalars().all()

async def get_formula(db: AsyncSession, formula_id: int, user_id: int):
    result = await db.execute(select(Formula).filter(Formula.id == formula_id, Formula.user_id == user_id))
    return result.scalar_one_or_none()

async def update_formula(db: AsyncSession, formula_id: int, formula: FormulaCreate, user_id: int):
    stmt = update(Formula).where(Formula.id == formula_id, Formula.user_id == user_id).values(**formula.dict())
    await db.execute(stmt)
    await db.commit()

async def delete_formula(db: AsyncSession, formula_id: int, user_id: int):
    stmt = delete(Formula).where(Formula.id == formula_id, Formula.user_id == user_id)
    await db.execute(stmt)
    await db.commit()
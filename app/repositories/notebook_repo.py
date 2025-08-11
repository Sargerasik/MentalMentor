from __future__ import annotations
from datetime import date
from typing import Optional, Sequence
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notebook_entry import NotebookEntry, MoodEnum

async def get(db: AsyncSession, entry_id: int) -> Optional[NotebookEntry]:
    return await db.get(NotebookEntry, entry_id)

async def get_by_date(db: AsyncSession, user_id: int, day: date) -> Optional[NotebookEntry]:
    res = await db.execute(select(NotebookEntry)
                           .where(and_(NotebookEntry.user_id == user_id,
                                       NotebookEntry.entry_date == day)))
    return res.scalar_one_or_none()

async def list_for_user(
    db: AsyncSession, user_id: int, *, limit: int = 50, offset: int = 0,
    date_from: Optional[date] = None, date_to: Optional[date] = None,
) -> Sequence[NotebookEntry]:
    stmt = select(NotebookEntry).where(NotebookEntry.user_id == user_id)
    if date_from:
        stmt = stmt.where(NotebookEntry.entry_date >= date_from)
    if date_to:
        stmt = stmt.where(NotebookEntry.entry_date <= date_to)
    stmt = stmt.order_by(desc(NotebookEntry.entry_date)).limit(limit).offset(offset)
    res = await db.execute(stmt)
    return res.scalars().all()

async def create(
    db: AsyncSession, *, user_id: int, entry_date: date, mood: MoodEnum,
    title: Optional[str], content: Optional[str],
) -> NotebookEntry:
    entry = NotebookEntry(
        user_id=user_id, entry_date=entry_date, mood=mood, title=title, content=content
    )
    db.add(entry)
    await db.flush()
    return entry

async def update(
    db: AsyncSession, entry: NotebookEntry, *, mood: Optional[MoodEnum],
    title: Optional[str], content: Optional[str],
) -> NotebookEntry:
    if mood is not None: entry.mood = mood
    if title is not None: entry.title = title
    if content is not None: entry.content = content
    await db.flush()
    return entry

async def delete(db: AsyncSession, entry: NotebookEntry) -> None:
    await db.delete(entry)
    await db.flush()

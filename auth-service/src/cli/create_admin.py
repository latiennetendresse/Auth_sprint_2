from asyncio import run as aiorun
from uuid import UUID

import typer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import async_session
from models.roles import Role, UserRole
from models.users import User


async def get_user_id(db: AsyncSession, email: str) -> UUID:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if user:
        print("Пользователь с таким email уже есть в базе.")
        return user.id

    password = typer.prompt(
        "Введите пароль для нового пользователя",
        hide_input=True,
        confirmation_prompt=True,
    )

    name = typer.prompt("Введите имя для нового пользователя")

    user = User(email=email, password=password, name=name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    print("Пользователь добавлен в базу.")
    return user.id


async def get_admin_role_id(db: AsyncSession) -> UUID:
    result = await db.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalars().first()

    if admin_role:
        print("Роль admin уже есть в базе.")
        return admin_role.id

    admin_role = Role(name="admin")
    db.add(admin_role)
    await db.commit()
    await db.refresh(admin_role)
    print("Роль admin добавлена в базу.")
    return admin_role.id


async def async_main():
    async with async_session() as db:
        email = typer.prompt("Введите email пользователя")
        user_id = await get_user_id(db, email)
        role_id = await get_admin_role_id(db)

        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id, UserRole.role_id == role_id
            )
        )
        user_role = result.scalars().first()

        if user_role:
            print("У пользователя уже есть роль admin.")
            return

        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
        await db.commit()
        print("Пользователю добавлена роль admin.")


def main():
    aiorun(async_main())


if __name__ == "__main__":
    typer.run(main)

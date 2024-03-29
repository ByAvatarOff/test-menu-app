"""Models"""
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Menu(Base):
    """ Model of view table menu"""
    __tablename__ = 'menu'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str]
    description: Mapped[str]

    submenus: Mapped[list['Submenu']] = relationship(cascade='all, delete-orphan')


class Submenu(Base):
    """Model of view table submenu"""
    __tablename__ = 'submenu'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str]
    description: Mapped[str]

    menu_id: Mapped[UUID] = mapped_column(ForeignKey('menu.id', ondelete='CASCADE'))
    dish: Mapped[list['Dish']] = relationship(cascade='all, delete-orphan')


class Dish(Base):
    """Model of view table dish"""
    __tablename__ = 'dish'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str]
    description: Mapped[str]
    price: Mapped[str]

    submenu_id: Mapped[UUID] = mapped_column(ForeignKey('submenu.id', ondelete='CASCADE'))

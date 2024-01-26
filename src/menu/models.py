from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.orm import declarative_base

import uuid


Base = declarative_base()


class Menu(Base):
    """
    Model of view table menu
    """
    __tablename__ = 'menu'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    description: Mapped[str]

    submenus: Mapped['Submenu'] = relationship(cascade='all, delete-orphan')


class Submenu(Base):
    """
    Model of view table submenu
    """
    __tablename__ = 'submenu'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    description: Mapped[str]

    menu_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('menu.id', ondelete='CASCADE'))
    dish: Mapped['Dish'] = relationship(cascade='all, delete-orphan')


class Dish(Base):
    """
    Model of view table dish
    """
    __tablename__ = 'dish'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    description: Mapped[str]
    price: Mapped[str]

    submenu_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('submenu.id', ondelete='CASCADE'))

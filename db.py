"""Module for handling database operations."""

import sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, Integer
from sqlalchemy import exc, and_
from sqlalchemy.dialects import postgresql

Base = declarative_base()


class Menu(Base):
    """Class for menus."""
    __tablename__ = 'menus'

    id = Column(Integer, primary_key=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    menu = Column(postgresql.JSONB, nullable=False)


def insert_menu(session, menus):
    """Inserts a menu into the database. Returns True on success and False
    on error."""
    if len(menus) == 0 or 'menu' not in menus[0]:
        return False

    start_date = min([min(menu['menu'].keys()) for menu in menus])
    end_date = max([max(menu['menu'].keys()) for menu in menus])

    menu = Menu(start_date=start_date, end_date=end_date, menu=menus)

    try:
        session.add(menu)
        session.commit()

        return True
    except exc.SQLAlchemyError as err:
        print('Error: menu insert failed: {0}'.format(err), file=sys.stderr)
        return False
    finally:
        session.close()


def get_menus(session, current_date):
    """Returns menus from the database which """

    try:
        query = session.query(Menu.menu).filter(and_(Menu.start_date <= current_date,
                                                     Menu.end_date >= current_date))
        return query.first()
    except exc.SQLAlchemyError as err:
        print('Error: menu query failed: {0}'.format(err))
        return None
    finally:
        session.close()

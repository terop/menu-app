"""Test module for menu-app."""
import configparser
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from menu import db


@pytest.fixture(scope='module')
def session(request):
    """Test setup function."""
    config = configparser.ConfigParser()
    # Ensure correct path to test configuration file
    cfg_file = 'test.cfg'
    if Path.cwd().name != 'test':
        cfg_file = 'test/{0}'.format(cfg_file)
    config.read(cfg_file)

    engine = create_engine(config['db']['DB_CON_STRING'])
    Session = sessionmaker(bind=engine)

    def finalizer():
        """Test finalizer which deletes all inserted rows."""
        session = Session()
        session.query(db.Menu).delete()
        session.commit()
        session.close()
        request.addfinalizer(finalizer)

    return Session()


class TestMenu:
    """Test class for menu-app."""

    def test_menu_insert_success(self, session):
        """Insert success test."""
        menu_data = [{'name': 'Amica TUAS',
                      'menu': {'2016-04-11': ['Keitettyjä perunoita (* ,G ,L ,M)',
                                              'Sitruunaisia kalapaloja (A ,L ,M)',
                                              'Yrttikermaviilikastiketta (A ,G ,L)']}}]
        assert db.insert_menu(session, menu_data)
        assert session.query(db.Menu).count() == 1

    def test_menu_insert_failure(self, session):
        """Insert failure test."""
        menu_data = [{'foobar'}]
        assert not db.insert_menu(session, {})
        assert not db.insert_menu(session, menu_data)

    def test_menu_get_menu_success(self, session):
        """Menu query success test."""
        # This test is dependent on the data inserted in the first test
        menu = db.get_menu(session, '2016-04-11')
        assert len(menu[0]) == 1
        assert menu[0][0]['name'] == 'Amica TUAS'

    def test_menu_get_menu_failure(self, session):
        """Menu query failure test."""
        # This test is dependent on the data inserted in the first test
        menu = db.get_menu(session, '2016-04-12')
        assert not menu
        menu = db.get_menu(session, '2016-04-13')
        assert not menu
        menu = db.get_menu(session, '2016-04-')
        assert not menu

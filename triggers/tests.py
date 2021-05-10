from django.db import connection
from pytest import fixture

from triggers.models import Book


@fixture
def book(db):
    return Book.objects.create(name='book')


@fixture
def simple_function():
    with open('pl_python/simple_function.sql', 'r') as f:
        return f.read()


def test_simple_function(simple_function, db):
    with connection.cursor() as cursor:
        cursor.execute(simple_function)
        cursor.execute('select pymax(10, 20)')
        row = cursor.fetchone()
    assert row[0] == 20

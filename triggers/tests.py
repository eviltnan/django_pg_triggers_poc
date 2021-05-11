from django.db import connection
from django.db.models import Func, Value, F
from pytest import fixture

from triggers.models import Book
from triggers.pl_python.builder import build_pl_python, install_function


@fixture
def book(db):
    return Book.objects.create(name='book')


@fixture
def simple_function_pl():
    with open('pl_python/simple_function.sql', 'r') as f:
        return f.read()


def test_simple_function(simple_function_pl, db):
    with connection.cursor() as cursor:
        cursor.execute(simple_function_pl)
        cursor.execute('select pymax(10, 20)')
        row = cursor.fetchone()
    assert row[0] == 20


def pymax(a: int,
          b: int) -> int:
    if a > b:
        return a
    return b


def test_generate_simple_pl_python_from_function(db):
    pl_python_function = build_pl_python(pymax)
    with connection.cursor() as cursor:
        cursor.execute(pl_python_function)
        cursor.execute('select pymax(10, 20)')
        row = cursor.fetchone()
    assert row[0] == 20


@fixture
def simple_function(db):
    install_function(pymax)


def test_call_simple_function_from_django_orm(simple_function, book):
    result = Book.objects.annotate(
        max_value=Func(F('amount_sold'), F('amount_stock'), function='pymax')
    )
    assert result[0].max_value == result[0].amount_stock

from pytest import fixture

from triggers.models import Book


@fixture
def book(db):
    return Book.objects.create(name='book')


def test_book(book):
    print(book)

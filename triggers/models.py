from django.db.models import Model, CharField, IntegerField

from triggers.pl_python.builder import plfunction


@plfunction
def pymax(a: int,
          b: int) -> int:
    if a > b:
        return a
    return b


class Book(Model):
    name = CharField(max_length=10)
    amount_stock = IntegerField(default=20)
    amount_sold = IntegerField(default=10)

from django.db.models import Model, CharField


class Book(Model):
    name = CharField(max_length=10)

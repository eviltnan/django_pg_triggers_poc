from django.contrib.postgres.operations import CreateExtension


class PythonExtension(CreateExtension):
    def __init__(self):
        self.name = 'plpython3u'

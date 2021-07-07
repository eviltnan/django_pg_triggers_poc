import inspect
from functools import wraps
from textwrap import dedent

from django.db import connection

type_mapper = {
    int: "integer"
}


def remove_decorator(source_code, name):
    start = source_code.find(f"@{name}")
    end = source_code.find("def")
    return source_code[:start] + source_code[end:]


def build_pl_function(f):
    name = f.__name__
    signature = inspect.signature(f)
    try:
        args = [
            f"{arg} {type_mapper[specs.annotation]}" for arg, specs in signature.parameters.items()
        ]
    except KeyError:
        raise RuntimeError(f"Function {f} must be fully annotated to be translated to pl/python")

    header = f"CREATE OR REPLACE FUNCTION {name} ({','.join(args)}) RETURNS {type_mapper[signature.return_annotation]}"

    body = remove_decorator(inspect.getsource(f), "plfunction")
    return f"""{header}
AS $$
{dedent(body)}
return {name}({','.join(signature.parameters.keys())})
$$ LANGUAGE plpython3u
"""


def build_pl_trigger_function(f, event, when, table):
    name = f.__name__

    header = f"CREATE OR REPLACE FUNCTION {name}() RETURNS TRIGGER"

    body = remove_decorator(inspect.getsource(f), "pltrigger")
    return f"""
BEGIN;
{header}
AS $$
{dedent(body)}
{name}(TD, plpy)
return 'MODIFY'
$$ LANGUAGE plpython3u;

DROP TRIGGER IF EXISTS {name + '_trigger'} ON {table} CASCADE; 
CREATE TRIGGER {name + '_trigger'}
{when} {event} ON {table}
FOR EACH ROW
EXECUTE PROCEDURE {name}();
END;
"""


def install_function(f, trigger_params=None):
    trigger_params = trigger_params or {}
    pl_python_function = build_pl_trigger_function(f, **trigger_params) if trigger_params else build_pl_function(f)
    with connection.cursor() as cursor:
        cursor.execute(pl_python_function)


pl_functions = {}
pl_triggers = {}


def plfunction(f):
    @wraps(f)
    def installed_func(*args, **kwargs):
        return f(*args, **kwargs)

    module = inspect.getmodule(installed_func)
    pl_functions[f"{module.__name__}.{installed_func.__qualname__}"] = installed_func
    return installed_func


def pltrigger(**trigger_parameters):
    def _pytrigger(f):
        @wraps(f)
        def installed_func(*args, **kwargs):
            return f(*args, **kwargs)

        module = inspect.getmodule(installed_func)
        pl_triggers[f"{module.__name__}.{installed_func.__qualname__}"] = installed_func, trigger_parameters
        return installed_func

    return _pytrigger

import inspect
from distutils.sysconfig import get_python_lib
from functools import wraps
from textwrap import dedent

from django.db import connection

type_mapper = {
    int: "integer",
    str: "varchar",
    inspect._empty: "void"
}


def remove_decorator(source_code, name):
    start = source_code.find(f"@{name}")
    end = source_code.find("def")
    if start < 0:
        return source_code
    return source_code[:start] + source_code[end:]


def build_pl_function(f):
    name = f.__name__
    signature = inspect.signature(f)
    try:
        args = []
        for arg, specs in signature.parameters.items():
            if specs.annotation not in type_mapper:
                raise RuntimeError(f"Unknown type {specs.annotation}")
            args.append(f"{arg} {type_mapper[specs.annotation]}")
    except KeyError as ex:
        raise RuntimeError(f"{ex}:"
                           f"Function {f} must be fully annotated to be translated to pl/python")

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


@plfunction
def pl_load_path(syspath: str):
    import sys
    sys.path.append(syspath)


def load_env():
    """
    Installs and loads the virtualenv of this project into the postgres interpreter.
    """
    install_function(pl_load_path)
    path = get_python_lib()
    with connection.cursor() as cursor:
        cursor.execute(f"select pl_load_path('{path}')")

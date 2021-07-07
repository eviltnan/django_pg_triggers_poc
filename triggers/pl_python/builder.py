import inspect
from functools import wraps
from textwrap import dedent

from django.db import connection

type_mapper = {
    int: "integer"
}


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

    body = inspect.getsource(f)
    body = body.replace("@plfunction", "")  # quick hack for now
    return f"""{header}
AS $$
{dedent(body)}
return {name}({','.join(signature.parameters.keys())})
$$ LANGUAGE plpython3u
"""


def build_pl_trigger_function(f, event, when, table):
    name = f.__name__

    header = f"CREATE OR REPLACE FUNCTION {name}() RETURNS TRIGGER"

    body = inspect.getsource(f)
    body = body.replace("@pltrigger", "")  # quick hack for now

    trigger = f"""
BEGIN;
CREATE TRIGGER {name + '_trigger'}
{when} {event} ON {table}
FOR EACH ROW
EXECUTE PROCEDURE {name}()
"""
    return f"""{header}
AS $$
{dedent(body)}
{name}(TD, plpy)
return 'MODIFY'
$$ LANGUAGE plpython3u;
{trigger};
END;
"""


def install_function(f, trigger=False):
    pl_python_function = build_pl_trigger_function() if trigger else build_pl_function(f)
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

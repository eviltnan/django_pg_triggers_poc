import inspect
from functools import wraps
from textwrap import dedent

from django.db import connection

type_mapper = {
    int: "integer"
}


def build_pl_python(f):
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
    body = body.replace("@plfunction", "") # quick hack for now
    return f"""{header}
AS $$
{dedent(body)}
return {name}({','.join(signature.parameters.keys())})
$$ LANGUAGE plpython3u
"""


def install_function(f):
    pl_python_function = build_pl_python(f)
    with connection.cursor() as cursor:
        cursor.execute(pl_python_function)


pl_functions = {}


def plfunction(f):
    @wraps(f)
    def installed_func(*args, **kwargs):
        return f(*args, **kwargs)
    module = inspect.getmodule(installed_func)
    pl_functions[f"{module.__name__}.{installed_func.__qualname__}"] = installed_func
    return installed_func

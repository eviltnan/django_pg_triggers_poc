import inspect

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

    header = f"CREATE FUNCTION {name} ({','.join(args)}) RETURNS {type_mapper[signature.return_annotation]}"
    raise Exception(header)

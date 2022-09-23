import os


def environ_get(key, default=None):
    retval = os.environ.get(key, default=default)

    if key not in os.environ:
        print(
            "environ_get: Env Var not defined! Using default! Attempted={}, default={}".format(
                key, default
            )
        )

    return retval


def environ_append(key, value, separator=" ", force=False):
    old_value = os.environ.get(key)
    if old_value is not None:
        value = old_value + separator + value
    os.environ[key] = value


def environ_prepend(key, value, separator=" ", force=False):
    old_value = os.environ.get(key)
    if old_value is not None:
        value = value + separator + old_value
    os.environ[key] = value


def environ_remove(key, value, separator=":", force=False):
    old_value = os.environ.get(key)
    if old_value is not None:
        old_value_split = old_value.split(separator)
        value_split = [x for x in old_value_split if x != value]
        value = separator.join(value_split)
    os.environ[key] = value


def environ_set(key, value):
    os.environ[key] = value


def path_append(value):
    if os.path.exists(value):
        environ_append("PATH", value, ":")


def path_prepend(value, force=False):
    if os.path.exists(value):
        environ_prepend("PATH", value, ":", force)

# inspired by boucanpy
from os.path import abspath, dirname, join

_utils_dir = abspath(dirname(__file__))


def _ajoin(target: str, path: str) -> str:
    return abspath(join(target, path))


# # smoke tests
# if __name__ == "__main__":
#     from upscale_cli.utils import paths

#     print(paths._utils_dir)
#     print(paths._ajoin("foo", "bar"))

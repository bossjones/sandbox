# pylint: disable=no-name-in-module
# SOURCE: https://github.com/aniketmaurya/tensorflow-fastapi-starter-pack/tree/master/application
from pydantic import BaseModel


class Symptom(BaseModel):
    fever: bool = False
    dry_cough: bool = False
    tiredness: bool = False
    breathing_problem: bool = False

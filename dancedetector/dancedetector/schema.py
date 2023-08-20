# pylint: disable=E0611

# pylint: disable=E0213

# Method should have "self" as first argument (no-self-argument)

# NOTE: fixes [pylint] No name 'BaseModel' in module 'pydantic'
# SOURCE: https://github.com/nokia-wroclaw/innovativeproject-sudoku/issues/39

# SOURCE: https://github.com/aniketmaurya/tensorflow-fastapi-starter-pack/tree/master/application
from pydantic import BaseModel


class Symptom(BaseModel):
    fever: bool = False
    dry_cough: bool = False
    tiredness: bool = False
    breathing_problem: bool = False

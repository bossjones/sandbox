"""
This type stub file was generated by pyright.
"""

__metaclass__ = type
class EnvironmentConfig:
    def __init__(self, distutils_section=..., **kw) -> None:
        ...
    
    def dump_variable(self, name): # -> None:
        ...
    
    def dump_variables(self): # -> None:
        ...
    
    def __getattr__(self, name):
        ...
    
    def get(self, name, default=...):
        ...
    
    def clone(self, hook_handler): # -> EnvironmentConfig:
        ...
    
    def use_distribution(self, dist): # -> None:
        ...
    



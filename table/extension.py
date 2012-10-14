class Extension:
  def __init__(self, name, *funcs):
    self.name = name
    self.funcs = funcs
  def apply(self, cls):
    for func in self.funcs:
      setattr(cls, func.func_name, func)


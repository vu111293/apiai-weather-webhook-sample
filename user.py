class Customer:
  "This is customer class"
  def __init__(self):
    self.cart = None
    pass

  def func(self):
	  pass

  @classmethod
  def from_dict(cls, dict):
    obj = cls()
    obj.__dict__.update(dict)
    return obj

  def jsonable(self):
    return self.__dict__



class Product:
  "This is product class"
  def __init__(self, name, number):
    self.name = name
    self.number = number
    pass
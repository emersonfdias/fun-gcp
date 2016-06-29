from protorpc import messages

class Greeting(messages.Message):
  """Greeting that stores a message."""
  message = messages.StringField(1)

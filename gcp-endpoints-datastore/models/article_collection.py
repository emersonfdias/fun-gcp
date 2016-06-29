from protorpc import messages
from models.article import Article

class ArticleCollection(messages.Message):
  items = messages.MessageField(Article, 1, repeated=True)

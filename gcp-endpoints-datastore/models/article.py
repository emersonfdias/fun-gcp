from protorpc import messages
from models.base import ModelBase
from google.appengine.ext import ndb

class Article(messages.Message):
	title = messages.StringField(1)
	author = messages.StringField(2)
	# date = messages.DateTimeField()
	# title = ndb.StringProperty()
	# title = ndb.StringProperty()
	# date = ndb.DateTimeProperty()

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from models.article import Article
from models.article_collection import ArticleCollection

# STORED_ARTICLES = ArticleCollection(items=[
#     Article(title='article 1!'),
#     Article(title='article 2!'),
# ])

article_api = endpoints.api(name='article', version='v1')

@article_api.api_class(resource_name='article')
class ArticleAPI(remote.Service):
  @endpoints.method(message_types.VoidMessage, ArticleCollection,
                    path='articles', http_method='GET',
                    name='articles.listArticles')
  def article_list(self, unused_request):
    query = Article.query()
    articles = []
    for article_model in query.fetch():
      article = Aticle(title=article_model.title,author=article_model.author)
      articles.append(article)

    return ArticleCollection(items=articles)

  ID_RESOURCE = endpoints.ResourceContainer(
      message_types.VoidMessage,
      id=messages.IntegerField(1, variant=messages.Variant.INT32))
  @endpoints.method(ID_RESOURCE, Article,
                    path='articles/{id}', http_method='GET',
                    name='articles.getArticles')
  def article_get(self, request):
    try:
      return STORED_ARTICLES.items[request.id]
    except (IndexError, TypeError):
      raise endpoints.NotFoundException('Greeting %s not found.' %
                                        (request.id,))

  MULTIPLY_METHOD_RESOURCE = endpoints.ResourceContainer(Article)
  @endpoints.method(MULTIPLY_METHOD_RESOURCE, Article,
                  path='articles', http_method='POST',
                  name='articles.create')
  def article_create(self, request):
    return Article(title=request.title)

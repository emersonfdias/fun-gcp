import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from models.greeting import Greeting
from models.greeting_collection import GreetingCollection

STORED_GREETINGS = GreetingCollection(items=[
    Greeting(message='hello world 2!'),
    Greeting(message='goodbye world 2!'),
])

issue_api = endpoints.api(name='issue', version='v1')

@issue_api.api_class(resource_name='issue')
class Issue(remote.Service):
  @endpoints.method(message_types.VoidMessage, GreetingCollection,
                    path='hellogreeting', http_method='GET',
                    name='greetings.listGreeting')
  def greetings_list(self, unused_request):
    return STORED_GREETINGS

  MULTIPLY_METHOD_RESOURCE = endpoints.ResourceContainer(
    Greeting,
    times=messages.IntegerField(2, variant=messages.Variant.INT32,
                                required=True))

  @endpoints.method(MULTIPLY_METHOD_RESOURCE, Greeting,
                  path='hellogreeting/{times}', http_method='POST',
                  name='greetings.multiply')
  def greetings_multiply(self, request):
    return Greeting(message=request.message * request.times)

  ID_RESOURCE = endpoints.ResourceContainer(
      message_types.VoidMessage,
      id=messages.IntegerField(1, variant=messages.Variant.INT32))

  @endpoints.method(ID_RESOURCE, Greeting,
                    path='hellogreeting/{id}', http_method='GET',
                    name='greetings.getGreeting')
  def greeting_get(self, request):
    try:
      return STORED_GREETINGS.items[request.id]
    except (IndexError, TypeError):
      raise endpoints.NotFoundException('Greeting %s not found.' %
                                        (request.id,))

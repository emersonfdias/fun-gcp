import endpoints

import helloworld_api

application = endpoints.api_server([helloworld_api.hw_api])
import random
import time
import json
import requests
import logging

logger = logging.getLogger(__name__)

class DiscoPy:

    _config = {
        "host": "https://discord.com/api",
        "path": {
            "validate": "/users/@me"
        }
    }


    def _post_helper(self, name):
        _config = self.__config
        url = f"{_config['host']}{_config['paths'][name]}"
        try:
            response = self._session.post(url, headers=self.HEADERS)
        except Exception as ex:
            raise f'Exception Raised :: {ex}'

        if self.debug:
            logger.debug(f"Response: {response.status_code} {response.content}")

        if response.status_code == 200:
            json_data = response.json()
            # print(json_data)
            if json_data['status'] == 'success':
                return response
            else:
                return [json.loads(response.text)]
        else:
            print(f"Invalid token: {self.token}")
            return json.loads(response.text)


    def __init__(self, token) -> None:
        self.token = token

        self.username = None
        self.id = None
        self.email = None
        self.phone = None
        self._session = requests.session()

        self.HEADERS = {"authorization": self.token, "content-type": "application/json"}
        self._validate()


    def _validate(self) -> None:
        """Internal function used to check if the provided discord token works or not"""

        r = self._post_helper('validate')
        print(f"Valid token: {self.token}")
        data = r.json()
        self.username = data['username'] + "#" + data['discriminator']
        self.id = data['id']
        self.email = data['email']
        self.phone = data['phone']
        
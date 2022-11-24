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
            "validate": "/users/@me",
            "messages": "/channels/",
            "get_messages": "/messages/search?offset=",
            "clear_messages": "/messages/search?author_id=",
            'delete_messages': "/messages/"
        }
    }


    def _get_helper(self, name, sub_path):

        _config = self._config

        if hasattr(self, 'channel_id'):
            if sub_path == 'get_messages':
                url = f"{_config['host']}{_config['path'][name]}{self.channel_id}{_config['path'][sub_path]}{self.offset}"
            elif sub_path == 'clear_messages':
                url = f"{_config['host']}{_config['path'][name]}{self.channel_id}{_config['host'][sub_path]}{self.id}"
        else:
            url = f"{_config['host']}{_config['path'][name]}"

        try:
            response = self._session.get(url, headers=self.HEADERS)
        except Exception as ex:
            raise f'Exception Raised :: {ex}'

        if response.status_code == 200:
            json_data = response.json()
            if json_data:
                return response
            else:
                return [json.loads(response.text)]
        else:
            print(f"Invalid token: {self.token}")
            return json.loads(response.text)
    

    def _del_helper(self, name, sub_path):

        _config = self._config

        if hasattr(self, 'channel_id') and hasattr(self, 'message_id'):
            if sub_path == 'delete_messages':
                url = f"{_config['host']}{_config['path'][name]}{self.channel_id}{_config['host'][sub_path]}{self.message_id}"
        else:
            url = f"{_config['host']}{_config['path'][name]}"

        try:
            response = self._session.delete(url, headers=self.HEADERS)
        except Exception as ex:
            raise f'Exception Raised :: {ex}'

        if response.status_code == 200:
            json_data = response.json()
            if json_data:
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

        r = self._get_helper('validate', False)
        print(f"Valid token: {self.token}")
        data = r.json()
        self.username = data['username'] + "#" + data['discriminator']
        self.id = data['id']
        self.email = data['email']
        self.phone = data['phone']
    

    def get_messages(self, channel_id: str, page: int = 0) -> list:
        """It will get 25 messages from a channel"""

        self.offset = 25 * page
        self.channel_id = channel_id
        r = self._get_helper('messages', 'get_messages')
        if r.status_code in [200, 201, 204]:
            return r.json()["messages"]
        else:
            return []


    def clear_messages(self, channel_id: str) -> None:
        """function to clear messages in a specific channel (specifed by giving a channel id number in str format)"""

        self.channel_id = channel_id
        total_messages = self._get_helper('messages', 'clear_messages').json()['total_results']
        page = 0
        total = 0
        while total <= total_messages:
            messages = self.get_messages(channel_id, page)
            for message in messages:
                if message[0]["author"]["id"] == self.id:
                    self.message_id = message[0]['id']
                    r = self._del_helper('messages', 'delete_messages')
                    print(r.status_code, r.text)
                    if r.status_code in [200, 201, 204]:
                        print(f"{self.username} | Deleted message {message[0]['id']}")
                        time.sleep(2)
                        total += 1
                    else:
                        print(r.status_code)
                        print(r.text)
            page += 1
        print(f"{self.username} | Deleted {total} messages in {channel_id}")
        

user = DiscoPy(token='')

import json
from channels.generic.websocket import WebsocketConsumer

class WebConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        print("Accepted new user")

        print("Generating pair")

    def disconnect(self, close_code):
        print("User disconnected")

    def send_data(self, data):
        pass

    def receive(self, text_data):
        data_json = json.loads(text_data)

        message = data_json['message']
        self.send(text_data=json.dumps({
            'message': message
            }))

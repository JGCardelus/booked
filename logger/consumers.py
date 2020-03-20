import json
from channels.generic.websocket import WebsocketConsumer

from data.models import User, Session
from booked.framework import Data_Checker, Data_Checker_Error

class LoginSocket(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        return super().disconnect(code)

    def receive(self, text_data=None, bytes_data=None):
        data_json = json.loads(text_data)

        try:
            Data_Checker(data_json, ["action", "username", "password"])
        except Data_Checker_Error:
            print("Data is corrupt.")
        else:
            if data_json["action"] == "verify":
                username = data_json["username"]
                password = data_json["password"]
                self.login(username, password)

    def login(self, username, password):
        access, user = User.verify(username, password)
        if access:
            session = Session.generate_session_key(user)
            self.send(json.dumps({
                'result': 'verified',
                'session_key': session.session_key
            }))
        else:
            self.send(json.dumps({
                'result': 'denied'
            }))

class SetupSocket(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        return super().disconnect(code)

    def receive(self, text_data=None, bytes_data=None):
        data_json = json.loads(text_data)
        try:
            Data_Checker(data_json, ["username", "name", "email", "password", "is_teacher"])
        except Data_Checker_Error as error:
            print("Data was corrupt")
            self.send(json.dumps({
                'result': 'denied'
                }))
        else:
            access, session = User.new(data_json)
            if access:
                self.send(json.dumps({
                'result': 'verified',
                'session_key': session.session_key
                }))
            else:
                self.send(json.dumps({
                'result': 'denied'
                }))

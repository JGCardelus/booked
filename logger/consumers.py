import json
from channels.generic.websocket import WebsocketConsumer

from data.models import User, Session
from booked.framework import Data_Checker, Data_Checker_Error, response_codes

class LoginSocket(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        return super().disconnect(code)

    def receive(self, text_data=None, bytes_data=None):
        data_json = json.loads(text_data)

        try:
            Data_Checker(data_json, ["request", "username", "password"])
        except Data_Checker_Error:
            print("Data is corrupt.")
        else:
            if data_json["request"] == "verify":
                username = data_json["username"]
                password = data_json["password"]
                self.login(username, password)

    def login(self, username, password):
        access, user = User.verify(username, password)
        if access:
            session = Session.generate_session(user)
            self.send(json.dumps({
                'response': 'verified',
                'code': response_codes.correct,
                'session_key': session.session_key
            }))
        else:
            self.send(json.dumps({
                'response': 'denied',
                'code': response_codes.error,
                'message': 'Invalid username or passoword'
            }))

class SetupSocket(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        return super().disconnect(code)

    def receive(self, text_data=None, bytes_data=None):
        data_json = json.loads(text_data)
        try:
            Data_Checker(data_json, ["request"])
        except Data_Checker_Error as error:
            print("Data was corrupt")
            self.send(json.dumps({
                'response': 'denied',
                'code': response_codes.error,
                'message': 'Data was incorrect'
                }))
        else:
            if data_json["request"] == "setup":
                self.setup(data_json)

        def setup(self, data):
            try:
                Data_Checker(data, ["username", "name", "email", "password", "is_teacher"])
            except Data_Checker_Error:
                print("Data was corrupt")

            access, session = User.new(data)
            if access:
                self.send(json.dumps({
                'response': 'verified',
                'code': response_codes.correct,
                'session_key': session.session_key
                }))
            else:
                self.send(json.dumps({
                'response': 'denied',
                'code': response_codes.error
                }))
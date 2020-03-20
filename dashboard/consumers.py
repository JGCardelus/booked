import json
from datetime import date, time
from channels.generic.websocket import WebsocketConsumer
from data.models import Meeting, Group, Session, Task
from booked.framework import Data_Checker, Data_Checker_Error, parser

class EventDistpatcher(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        return super().disconnect(code)

    def receive(self, text_data=None, bytes_data=None):
        data_json = json.loads(text_data)

        try:
            Data_Checker(data_json, ["request", "session_key", "date", "time", "groups"], can_be_empty=True)
        except Data_Checker_Error:
            # Send error message
            pass
        else:
            if data_json["request"] == 'meetings':
                self.dispatch_mettings(data_json)
            if data_json["request"] == 'tasks':
                self.dispatch_tasks(data_json)

    def get_user_data(self, session_key):
        session = Session.get_session(session_key)
        if session != None:
            user = session.user
            groups = Group.get_groups(user)

            return session, user, groups

        return None, None, None

    def dispatch_mettings(self, data):
        session, user, groups = self.get_user_data(data["session_key"])

        if session == None or user == None or groups == None:
            message = {
                "response": "meetings",
                "data": {}
            }
            self.send(json.dumps(message))

        else:
            meetings = []

            date = parser.parse_date(str(data["date"]))
            time = parser.parse_time(str(data["time"]))

            search_groups = data["groups"]
            for group in groups:
                if search_groups != None:
                    if group.group_id in search_groups:
                        continue
                group_meetings = Meeting.get_meetings(group, date, time)
                meetings.extend(group_meetings)
            
            meetings_json = parser.parse_meetings(meetings)
            message = {
                "response": "meetings",
                "data": meetings_json
            }
            
            self.send(json.dumps(message))

    def dispatch_tasks(self, data):
        session, user, groups = self.get_user_data(data["session_key"])

        if session == None or user == None or groups == None:
            message = {
                "response": "tasks",
                "data": {}
            }
            self.send(json.dumps(message))

        else:
            tasks = []

            date = parser.parse_date(str(data["date"]))
            time = parser.parse_time(str(data["time"]))
            name = data["name"]

            search_groups = data["groups"]
            for group in groups:
                if search_groups != None:
                    if group.group_id in search_groups:
                        continue
                group_tasks = Task.get_tasks(group, date, time, name)
                tasks.extend(group_tasks)
            
            tasks_json = parser.parse_tasks(tasks)
            message = {
                "response": "tasks",
                "data": tasks_json
            }
            
            self.send(json.dumps(message))

        
        
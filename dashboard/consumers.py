import json
from datetime import date, time
from channels.generic.websocket import WebsocketConsumer
from data.models import Meeting, JoinedGroup, Session, Task
from booked.framework import Data_Checker, Data_Checker_Error, parser, response_codes

class UserData:
    def __init__(self, session, user, groups):
        self.session = session
        self.user = user
        self.groups = groups

class EventDistpatcher(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        return super().disconnect(code)

    def receive(self, text_data=None, bytes_data=None):
        data_json = json.loads(text_data)

        try:
            Data_Checker(data_json, ["request", "data", "session_key"], can_be_empty=True)
        except Data_Checker_Error:
            # Send error message
            pass
        else:
            data_requested = data_json["data"]
            request = data_json["request"]

            if data_requested == 'meetings':
                if request == "filter":
                    self.get_meetings_by_datetime(data_json)
                if request == 'more':
                    self.get_meetings_more(data_json)
                if request == 'range':
                    self.get_meetings_by_range(data_json)
            if data_requested == 'tasks':
                if request == "filter":
                    self.get_tasks_by_datetime(data_json)
                if request == 'more':
                    self.get_tasks_more(data_json)
                if request == 'range':
                    self.get_tasks_by_range(data_json)
            if data_requested == 'handshake':
                self.get_isadmin_value(data_json)

    def build_response(self, response, code, data):
        message_json = {
            "response": response,
            "code": code,
            "data": data
        }
        
        message = json.dumps(message_json)
        return message

    def verify_request(self, data, expected_keys, can_be_empty=False):
        # Check for errors in the message
        try:
            Data_Checker(data, expected_keys, can_be_empty=can_be_empty)
        except Data_Checker_Error:
            message = self.build_response(data["data"], response_codes.error, [])
            self.send(message)
            return False

        session_key = data["session_key"]
        user_data = self.get_user_data(session_key)

        # Check for errors in the user, session or groups
        if user_data == None:
            message = self.build_response(data["data"], response_codes.error, [])
            self.send(message)
            return False, None

        return True, user_data

    def get_isadmin_value(self, data):
        is_valid, user_data = self.verify_request(data, [])
        if not is_valid: return

        user = user_data.user
        is_admin = user.is_admin

        message = self.build_response(data["data"], response_codes.correct, is_admin)
        self.send(message)

    def get_user_data(self, session_key):
        session = Session.get_session(session_key)
        if session != None:
            user = session.user
            groups = []
            joined_groups = JoinedGroup.get_groups(user)
            for joined_group in joined_groups:
                groups.append(joined_group.group) 
            if groups == []:
                return None

            user_data = UserData(session, user, groups)
            return user_data

        return None

    def get_meetings_by_datetime(self, data):
        is_valid, user_data = self.verify_request(data, ["date", "time", "groups"])
        if not is_valid: return

        groups = user_data.groups

        # Get information from json
        date = parser.parse_date(str(data["date"]))
        time = parser.parse_time(str(data["time"]))
        search_groups = data["groups"]
        
        meetings = self.apply_meetings_filter(search_groups, groups, date, time)
        # Parse meetings
        meetings_json = parser.parse_meetings(meetings)
        message = self.build_response('meetings', response_codes.correct, meetings_json)
        # Send
        self.send(message)

    def apply_meetings_filter(self, search_groups, groups, date, time):
        meetings = []
        for group in groups:
            # Apply group_id filter
            if search_groups != None:
                if group.group_id in search_groups:
                    continue
            
            # Apply other filters
            group_meetings = Meeting.get_by_datetime(group, date, time)
            meetings.extend(group_meetings)

        return meetings

    def get_tasks_by_datetime(self, data):
        is_valid, user_data = self.verify_request(data, ["date", "time", "groups", "name"])
        if not is_valid: return
        groups = user_data.groups

        date = parser.parse_date(str(data["date"]))
        time = parser.parse_time(str(data["time"]))
        name = data["name"]
        
        search_groups = data["groups"]
        
        tasks = self.apply_tasks_filters(search_groups, name, groups, date, time)
        tasks_json = parser.parse_tasks(tasks)
        
        message = self.build_response('tasks', response_codes.correct, tasks_json)
        
        self.send(message)

    def apply_tasks_filters(self, search_groups, name, groups, date, time):
        tasks = []
        for group in groups:
            if search_groups != None:
                if group.group_id in search_groups:
                    continue
            group_tasks = Task.get_by_datetime(group, name, date, time)
            tasks.extend(group_tasks)

        return tasks
        
    def get_meetings_more(self, data):
        is_valid, user_data = self.verify_request(data, ["n", "date", "time", "meeting_id", "groups"])
        if not is_valid: return

        # Buil data
        groups = user_data.groups
        n = int(data["n"])
        date = parser.parse_date(data["date"])
        time = parser.parse_time(data["time"])
        date_b = parser.parse_date('%-%-%')
        time_b = parser.parse_time('%:%')
        meeting_id = data["meeting_id"]
        search_groups = data["groups"]

        meetings_in_range = self.apply_range_in_meetings(search_groups, groups, date, time, date_b, time_b)
        meetings = self.apply_count_restriction_in_meetings(meetings_in_range, meeting_id, n)
        meetings_json = parser.parse_meetings(meetings)
        message = self.build_response(data["data"], response_codes.correct, meetings_json)
        self.send(message)

    def apply_count_restriction_in_meetings(self, meetings_in_range, meeting_id, n):
        meetings = []
        recording = False
        for meeting_in_range in meetings_in_range:
            if recording:
                meetings.append(meeting_in_range)

            if meeting_in_range.meeting_id == meeting_id:
                recording = True

        if len(meetings) > n:
            meetings = meetings[:n]

        return meetings

    def get_tasks_more(self, data):
        is_valid, user_data = self.verify_request(data, ["n", "date", "time", "task_id", "groups", "name"])
        if not is_valid: return

        # Buil data
        groups = user_data.groups
        n = int(data["n"])
        date = parser.parse_date(data["date"])
        time = parser.parse_time(data["time"])
        date_b = parser.parse_date('%-%-%')
        time_b = parser.parse_time('%:%')
        task_id = data["task_id"]
        search_groups = data["groups"]
        name = data["name"]

        tasks_in_range = self.apply_range_in_tasks(search_groups, groups, name, date, time, date_b, time_b)
        tasks = self.apply_count_restriction_in_task(tasks_in_range, task_id, n)
        tasks_json = parser.parse_meetings(tasks)
        message = self.build_response(data["data"], response_codes.correct, tasks_json)
        self.send(message)

    def apply_count_restriction_in_tasks(self, tasks_in_range, task_id, n):
        tasks = []
        recording = False
        for task_in_range in tasks_in_range:
            if recording:
                tasks.append(task_in_range)

            if task_in_range.group_id == task_id:
                recording = True

        if len(tasks) > n:
            tasks = tasks[:n]

        return tasks

    def get_meetings_by_range(self, data):
        is_valid, user_data = self.verify_request(data, ["date_a", "time_a", "date_b", "time_b", "groups"])
        if not is_valid: return

        date_a = parser.parse_date(data["date_a"])
        date_b = parser.parse_date(data["date_b"])

        time_a = parser.parse_time(data["time_a"])
        time_b = parser.parse_time(data["time_b"])

        search_groups = data["groups"]
        groups = user_data.groups

        meetings = self.apply_range_in_meetings(search_groups, groups, date_a, time_a, date_b, time_b)
        meetings_json = parser.parse_meetings(meetings)
        message = self.build_response(data["data"], response_codes.correct, meetings_json)
        
        self.send(message)

    def apply_range_in_meetings(self, search_groups, groups, date_a, time_a, date_b, time_b):
        meetings = []
        for group in groups:
            if search_groups != None:
                if group.group_id in search_groups:
                    continue
            group_meetings = Meeting.get_by_range(group, date_a, time_a, date_b, time_b)
            meetings.extend(group_meetings)

        return meetings

    def get_tasks_by_range(self, data):
        is_valid, user_data = self.verify_request(data, ["date_a", "time_a", "date_b", "time_b", "groups", "name"])
        if not is_valid: return

        date_a = parser.parse_date(data["date_a"])
        date_b = parser.parse_date(data["date_b"])

        time_a = parser.parse_time(data["time_a"])
        time_b = parser.parse_time(data["time_b"])

        search_groups = data["groups"]
        name = data["name"]
        groups = user_data.groups

        tasks = self.apply_range_in_tasks(search_groups, groups, name, date_a, time_a, date_b, time_b)
        tasks_json = parser.parse_tasks(tasks)
        message = self.build_response(data["data"], response_codes.correct, tasks_json)
        self.send(message)

    def apply_range_in_tasks(self, search_groups, groups, name, date_a, time_a, date_b, time_b):
        tasks = []
        for group in groups:
            if search_groups != None:
                if group.group_id in search_groups:
                    continue
            group_tasks = Task.get_by_range(group, name, date_a, time_a, date_b, time_b)
            tasks.extend(group_tasks)

        return tasks
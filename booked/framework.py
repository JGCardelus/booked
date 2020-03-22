import datetime

class Data_Checker_Error(Exception):
    def __init___(self, error_message):
        Exception.__init__(self, "Data_Checker_Error: The data was incorrect. Error message: " % error_message)
        print(error_message)
        self.error_message = error_message

class Data_Checker:
    def __init__(self, data, keys, can_be_empty=False):
        self.data = data
        self.keys = keys

        is_empty = self.is_empty()
        if is_empty:
            raise Data_Checker_Error("Data is None or empty")

        has_expected_keys = self.has_expected_keys()
        if not has_expected_keys:
            raise Data_Checker_Error("Data does not contain the specified keys")

        if not can_be_empty:
            has_empty_items = self.check_for_empty_items()
            if has_empty_items:
                raise Data_Checker_Error("Data conatins empty values")

    def check_for_empty_items(self):
        for elem in self.data.items():
            val = elem[1]
            if isinstance(val, str):
                if not val:
                    return True
                
                has_only_whitespaces = True
                for char in val:
                    if char != ' ':
                        has_only_whitespaces = False

                if has_only_whitespaces:
                    return True

        return False

    def has_expected_keys(self):
        has_keys = True
        for key in self.keys:
            if key not in self.data.keys():
                has_keys = False
                break

        return has_keys

    def is_empty(self):
        if self.data == None:
            return True
        if self.data == '':
            return True
        else:
            return False

class Parser:
    def parse_date(self, raw_date):
        date = self.parse_datetime(raw_date, '-')
        return date

    def parse_time(self, raw_time):
        time = self.parse_datetime(raw_time, ':')
        return time

    def parse_datetime(self, raw_elem, separator):
        raw_elem_chunks = raw_elem.split(separator)
        elem = []
        for raw_date_chunk in raw_elem_chunks:
            if raw_date_chunk == '%':
                elem.append(None)
            else:
                elem.append(int(raw_date_chunk))

        return elem

    def parse_datetime_object(self, datetime_obj):
        datetime_obj_primary_chunks = datetime_obj.split('+')
        datetime_obj_chunks = datetime_obj_primary_chunks[0].split(' ')

        date = self.parse_date(datetime_obj_chunks[0])
        time = self.parse_time(datetime_obj_chunks[1])

        return date, time

    def parse_meetings(self, meetings):
        meetings_json = {}
        for meeting in meetings:
            meeting_json = self.parse_meeting(meeting)
            meetings_json[meeting.meeting_id] = meeting_json

        return meetings_json

    def parse_meeting(self, meeting):
        meeting_json = {
            "group_id": meeting.group.group_id,
            "group_name": meeting.group.name,
            "time": str(meeting.time),
            "duration": str(meeting.duration),
            "description": meeting.description,
            "links": meeting.links
        }

        return meeting_json

    def parse_tasks(self, tasks):
        tasks_json = {}
        for task in tasks:
            task_json = self.parse_task(task)
            tasks_json[task.task_id] = task_json

        return tasks_json

    def parse_task(self, task):
        task_json = {
            "group_id": task.group.group_id,
            "group_name": task.group.name,
            "name": task.name,
            "due_date": str(task.due_date),
            "notes": task.notes
        }

        return task_json

class DateTime_Filter:
    def apply(self, date_a, time_a, eval_date, eval_time):
        is_valid = True

        for i in range(3):
            if date_a[i] != None:
                if date_a[i] != eval_date[i]:
                    is_valid = False

        for i in range(2):
            if time_a[i] != None:
                if time_a[i] != eval_time[i]:
                    is_valid = False

        return is_valid

    def apply_range(self, date_a, time_a, date_b, time_b, eval_date, eval_time):
        is_valid = True

        for i in range(3):
            if date_a[i] != None:
                if eval_date[i] < date_a[i]:
                    is_valid = False

            if date_b[i] != None:
                if eval_date[i] > date_b[i]:
                    is_valid = False

        for i in range(2):
            if time_a[i] != None:
                if eval_time[i] < time_a[i]:
                    is_valid = False
            if time_b[i] != None:
                if eval_time[i] > time_b[i]:
                    is_valid = False

        return is_valid

class ResponseCodes:
    def __init__(self):
        self.error = "ERROR"
        self.correct = "VALID"

dt_filter = DateTime_Filter()
parser = Parser()
response_codes = ResponseCodes()
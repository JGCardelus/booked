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

        has_keys = self.has_keys()
        if not has_keys:
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

    def has_keys(self):
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
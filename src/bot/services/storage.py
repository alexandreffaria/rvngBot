class Storage:
    def __init__(self):
        self.data = {}

    def set(self, user_id, key, value):
        if user_id not in self.data:
            self.data[user_id] = {}
        self.data[user_id][key] = value

    def get(self, user_id, key, default=None):
        return self.data.get(user_id, {}).get(key, default)

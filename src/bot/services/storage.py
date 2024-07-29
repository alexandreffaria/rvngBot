class Storage:
    def __init__(self, database):
        self.database = database

    def set(self, user_id, key, value):
        self.database.set_storage_data(user_id, key, value)

    def get(self, user_id, key, default=None):
        return self.database.get_storage_data(user_id, key, default)
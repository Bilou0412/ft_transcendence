class UserInfo:
    def __init__(self, id, username, blocked=None):
        self.id = id
        self.username = username
        self.blocked = blocked if isinstance(blocked, list) else []

    def addBlocked(self, username):
        self.blocked.append(username)

    def delBlocked(self, username):
        self.blocked.pop(username)

import uuid


class SessionManager():
    def __init__(self):
        self._sessions = {}  # session_id: username

    @property
    def sessions(self):
        return self._sessions

    def get_username_for_session_id(self, session_id):
        username = self.sessions.get(session_id)
        return username

    def generate_session_id_for_user(self, username):
        session_id = self._generate_session_id()
        # Ensure the session ID does not already exist.
        while session_id in self.sessions:
            session_id = self._generate_session_id()
        self.sessions[session_id] = username
        return session_id

    def _generate_session_id(self):
        return uuid.uuid4()

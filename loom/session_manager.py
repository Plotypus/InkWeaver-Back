import uuid


class SessionManager():
    def __init__(self):
        self._sessions = {}  # session_id: user_id

    @property
    def sessions(self):
        return self._sessions

    def get_user_id_for_session_id(self, session_id):
        user_id = self.sessions.get(session_id)
        return user_id

    def generate_session_id_for_user(self, user_id):
        session_id = self._generate_session_id()
        # Ensure the session ID does not already exist.
        while session_id in self.sessions:
            session_id = self._generate_session_id()
        self.sessions[session_id] = user_id
        return session_id

    @staticmethod
    def _generate_session_id():
        return str(uuid.uuid4())

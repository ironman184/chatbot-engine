def get_session(SESSIONS, sessionId):
    return SESSIONS.get(sessionId, {})

def save_session(SESSIONS, sessionId, session):
    SESSIONS[sessionId] = session

def clear_session(SESSIONS, sessionId):
    if sessionId in SESSIONS:
        del SESSIONS[sessionId]

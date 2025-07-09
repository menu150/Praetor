from enum import Enum
from datetime import datetime

class MemoryType(str, Enum):
    CHAT = "chat"
    API_CALL = "api_call"
    TASK = "task"
    REFLECTION = "reflection"
    USER_PREF = "user_pref"

class RetentionPolicy(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"

def new_memory_item(type, content, tags=[], retention="episodic", meta={}):
    return {
        "id": str(uuid.uuid4()),
        "type": type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "content": content,
        "tags": tags,
        "summary": None,
        "embedding": None,
        "retention": retention,
        "meta": meta
    }

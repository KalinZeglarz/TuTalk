import json
import uuid
import time
from enum import Enum
from typing import Dict, Any


class MessageType(Enum):
    MESSAGE = "message"
    HELLO = "hello"
    LEAVE = "leave"


def now() -> str:
    return time.strftime("%H:%M:%S")


def make_message(sender: str, content: str) -> Dict[str, Any]:
    return {
        "type": MessageType.MESSAGE.value,
        "id": str(uuid.uuid4()),
        "sender": sender,
        "content": content,
        "time": now()
    }


def make_hello(sender: str) -> Dict[str, Any]:
    return {
        "type": MessageType.HELLO.value,
        "sender": sender,
        "time": now()
    }


def make_leave(sender: str) -> Dict[str, Any]:
    return {
        "type": MessageType.LEAVE.value,
        "sender": sender,
        "time": now()
    }


def encode(obj: Dict[str, Any]) -> bytes:
    return (json.dumps(obj) + "\n").encode('utf-8')


def decode(line: str) -> Dict[str, Any]:
    return json.loads(line)

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class Conversation:
    id: str
    title: str
    create_time: int
    update_time: int
    conversation_id: Optional[str] = None
    is_archived: bool = False
    is_starred: bool = False
    default_model_slug: Optional[str] = None

@dataclass
class Message:
    id: str
    conversation_id: str
    author_role: str
    content: str
    create_time: int
    parent_id: Optional[str] = None
    children: List[str] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {} 
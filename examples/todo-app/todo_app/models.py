"""Todo 数据模型。"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class Priority(Enum):
    """待办优先级。"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Todo:
    """待办事项模型。"""

    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: Optional[str] = None
    completed: bool = False
    priority: Priority = Priority.MEDIUM
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """转换为字典。"""
        data = asdict(self)
        data["priority"] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Todo":
        """从字典创建 Todo。"""
        data = data.copy()
        if isinstance(data.get("priority"), str):
            data["priority"] = Priority(data["priority"])
        return cls(**data)

    def mark_complete(self) -> None:
        """标记为完成。"""
        self.completed = True
        self.updated_at = datetime.now().isoformat()

    def update(self, **kwargs) -> None:
        """更新字段。"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ("id", "created_at"):
                if key == "priority" and isinstance(value, str):
                    value = Priority(value)
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()

    def __str__(self) -> str:
        """格式化输出。"""
        status = "✓" if self.completed else "○"
        priority_icons = {
            Priority.HIGH: "🔴",
            Priority.MEDIUM: "🟡",
            Priority.LOW: "🟢",
        }
        icon = priority_icons.get(self.priority, "")
        return f"[{self.id}] {status} {icon} {self.title}"

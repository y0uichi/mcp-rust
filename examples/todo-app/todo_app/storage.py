"""JSON 文件存储。"""

import json
from pathlib import Path
from typing import List

from .models import Todo


class JsonStorage:
    """JSON 文件存储类。"""

    def __init__(self, file_path: str = "todos.json"):
        """初始化存储。

        Args:
            file_path: JSON 文件路径
        """
        self.file_path = Path(file_path)

    def load(self) -> List[Todo]:
        """加载所有待办。

        Returns:
            待办列表
        """
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Todo.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"警告: 加载数据失败 - {e}")
            return []

    def save(self, todos: List[Todo]) -> None:
        """保存所有待办。

        Args:
            todos: 待办列表
        """
        data = [todo.to_dict() for todo in todos]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def clear(self) -> None:
        """清空存储。"""
        if self.file_path.exists():
            self.file_path.unlink()

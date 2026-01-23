"""Todo 管理器 - 处理 CRUD 操作。"""

from typing import List, Optional

from .models import Todo, Priority
from .storage import JsonStorage


class TodoManager:
    """待办管理器。"""

    def __init__(self, storage: Optional[JsonStorage] = None):
        """初始化管理器。

        Args:
            storage: 存储实例，默认使用 JsonStorage
        """
        self.storage = storage or JsonStorage()
        self._todos: List[Todo] = []
        self._load()

    def _load(self) -> None:
        """从存储加载数据。"""
        self._todos = self.storage.load()

    def _save(self) -> None:
        """保存数据到存储。"""
        self.storage.save(self._todos)

    def add(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium"
    ) -> Todo:
        """添加新待办。

        Args:
            title: 标题
            description: 描述
            priority: 优先级 (high/medium/low)

        Returns:
            新创建的 Todo
        """
        todo = Todo(
            title=title,
            description=description,
            priority=Priority(priority),
        )
        self._todos.append(todo)
        self._save()
        return todo

    def list(self, show_completed: bool = False) -> List[Todo]:
        """列出待办。

        Args:
            show_completed: 是否包含已完成的

        Returns:
            待办列表
        """
        if show_completed:
            return self._todos
        return [t for t in self._todos if not t.completed]

    def get(self, todo_id: str) -> Optional[Todo]:
        """获取单个待办。

        Args:
            todo_id: 待办 ID

        Returns:
            Todo 或 None
        """
        for todo in self._todos:
            if todo.id == todo_id or todo.id.startswith(todo_id):
                return todo
        return None

    def complete(self, todo_id: str) -> Optional[Todo]:
        """标记待办为完成。

        Args:
            todo_id: 待办 ID

        Returns:
            更新后的 Todo 或 None
        """
        todo = self.get(todo_id)
        if todo:
            todo.mark_complete()
            self._save()
        return todo

    def remove(self, todo_id: str) -> bool:
        """删除待办。

        Args:
            todo_id: 待办 ID

        Returns:
            是否删除成功
        """
        todo = self.get(todo_id)
        if todo:
            self._todos.remove(todo)
            self._save()
            return True
        return False

    def update(self, todo_id: str, **kwargs) -> Optional[Todo]:
        """更新待办。

        Args:
            todo_id: 待办 ID
            **kwargs: 要更新的字段

        Returns:
            更新后的 Todo 或 None
        """
        todo = self.get(todo_id)
        if todo:
            todo.update(**kwargs)
            self._save()
        return todo

    def clear_completed(self) -> int:
        """清除所有已完成的待办。

        Returns:
            删除的数量
        """
        original_count = len(self._todos)
        self._todos = [t for t in self._todos if not t.completed]
        self._save()
        return original_count - len(self._todos)

    @property
    def stats(self) -> dict:
        """获取统计信息。"""
        total = len(self._todos)
        completed = sum(1 for t in self._todos if t.completed)
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
        }

"""Tests for app.service (substrate repository)."""
import unittest

from app.service import TaskService


class TaskServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = TaskService()

    def test_create_assigns_sequential_ids(self):
        first = self.service.create("write benchmark")
        second = self.service.create("publish report")
        self.assertEqual((first.task_id, second.task_id), (1, 2))

    def test_create_trims_title(self):
        self.assertEqual(self.service.create("  padded  ").title, "padded")

    def test_create_rejects_blank_title(self):
        with self.assertRaises(ValueError):
            self.service.create("   ")

    def test_complete_marks_task_done(self):
        task = self.service.create("finish")
        self.assertTrue(self.service.complete(task.task_id).done)

    def test_complete_unknown_task_raises(self):
        with self.assertRaises(KeyError):
            self.service.complete(99)

    def test_pending_excludes_completed(self):
        keep = self.service.create("keep")
        drop = self.service.create("drop")
        self.service.complete(drop.task_id)
        self.assertEqual([task.task_id for task in self.service.pending()], [keep.task_id])

    def test_get_returns_none_for_unknown(self):
        self.assertIsNone(self.service.get(42))


if __name__ == "__main__":
    unittest.main()

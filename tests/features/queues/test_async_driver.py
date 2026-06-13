from tests import TestCase
from src.masonite.queues import Queueable
import os
import time


from tests.integrations.app.SayHi import SayHello


class FailingJob(Queueable):
    def __init__(self):
        self.captured = None

    def handle(self):
        # Raise an error a few frames deep so the traceback is meaningful.
        return self._explode()

    def _explode(self):
        raise ValueError("boom")

    def failed(self, obj, e):
        self.captured = e


class TestAsyncDriver(TestCase):
    def test_async_push(self):
        self.application.make("queue").push(SayHello(), driver="async")

    def test_failed_job_receives_full_traceback(self):
        job = FailingJob()
        self.application.make("queue").push(job, driver="async", blocking=True)

        # The failed callback should receive the full traceback, including the
        # originating frame, not only the exception message.
        self.assertIsNotNone(job.captured)
        self.assertIn("Traceback (most recent call last)", job.captured)
        self.assertIn("_explode", job.captured)
        self.assertIn("ValueError: boom", job.captured)

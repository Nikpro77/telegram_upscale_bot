import asyncio

class QueueManager:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.processing = set()

    async def add_task(self, user_id, coro):
        if user_id in self.processing:
            return False  # User already has a task processing
        await self.queue.put((user_id, coro))
        return True

    async def worker(self):
        while True:
            user_id, coro = await self.queue.get()
            self.processing.add(user_id)
            try:
                await coro()
            except Exception:
                pass
            self.processing.remove(user_id)
            self.queue.task_done()

queue_manager = QueueManager()

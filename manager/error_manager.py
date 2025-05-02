# manager/error_manager.py

import logging

class ErrorManager:
    @staticmethod
    async def handle_error(e):
        logging.error(f"Error occurred: {e}")
        await asyncio.sleep(1)
"""
generic utils for the application
"""
import asyncio
import logging
from typing import Tuple


class SingletonMeta(type):
    """
    Singleton Meta Class
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class AsyncSubProcessMixin:
    """
    Mixin to provide a common implementation to run processes
    """
    _logger: logging.Logger

    async def _execute_subprocess(self, command: str) -> Tuple[str, str, bool]:
        """execute a subprocess at system level

        :param command: command to execute
        :type command: str
        :return: stdout, stderr, success
        :rtype: Tuple[str, str, bool]
        """
        success_state = True
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        self._logger.debug(f"[{command!r} exited with {proc.returncode}]")
        if stdout:
            stdout = stdout.decode()
            self._logger.debug(f"standard-out of '{command}':\n{stdout}")

        if stderr:
            stderr = stderr.decode()
            self._logger.debug(f"standard-err of '{command}':\n{stderr}")

        if proc.returncode > 0:
            self._logger.error(f"unable to execute command '{command}': {proc.returncode}")
            success_state = False

        return stdout, stderr, success_state

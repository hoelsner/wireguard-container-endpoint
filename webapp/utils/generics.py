"""
generic utils for the application
"""
import logging
from typing import Tuple

import utils.config
import utils.os_func


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
    Mixin to provide a common implementation to run processes on OS level
    """
    _logger: logging.Logger

    async def _execute_subprocess(self, command: str) -> Tuple[str, str, bool]:
        """execute a subprocess at os level

        :param command: command to execute
        :type command: str
        :return: stdout, stderr, success
        :rtype: Tuple[str, str, bool]
        """
        # skip command execution when unit-testing
        stdout, stderr, success_state = utils.os_func.run_subprocess(
            command=command,
            logger=self._logger
        )
        if stdout != "":
            self._logger.debug(f"standard-out of '{command}':\n{stdout}")

        if stderr != "":
            self._logger.debug(f"standard-err of '{command}':\n{stderr}")

        return stdout, stderr, success_state

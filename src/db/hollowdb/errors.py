from abc import ABC, abstractmethod


class Error(ABC, Exception):
    """
    Abstract base class for custom exceptions.

    This class provides a common interface for all custom exceptions
    and ensures that each exception class has a name, message, and helper attribute.
    """

    def __init__(self, message: str, helper: str):
        """
        Initialize an Error instance.

        Args:
            message (str): The error message.
            helper (str): A helper message providing additional information or guidance.
        """
        super().__init__(message)
        self.name = self.__class__.__name__
        self.message = message
        self.helper = helper

    @abstractmethod
    def throw(self) -> str:
        """
        Create and return a formatted error message.

        Returns:
            str: A formatted error message with the error name, message, and helper.
        """
        pass


class AuthError(Error):
    """
    Exception class for authentication-related errors.
    """

    def throw(self) -> str:
        """
        Create and return a formatted AuthError message.

        Returns:
            str: A formatted AuthError message with the error name, message, and helper.
        """
        return f"{self.name}: {self.message}\nHelper: {self.helper}"


class HollowDBError(Error):
    """
    Exception class for errors related to the HollowDB database.
    """

    def throw(self) -> str:
        """
        Create and return a formatted HollowDBError message.

        Returns:
            str: A formatted HollowDBError message with the error name, message, and helper.
        """
        return f"{self.name}: {self.message}\nHelper: {self.helper}"

class WakuClientError(Exception):
    """Base class for Waku client exceptions."""


class WakuSubscriptionError(WakuClientError):

    def __init__(self, msg: str):
        """
        Raised when there is an error subscribing to a topic.

        Args:
            msg (str): The exception message.
        """

        super().__init__(msg)


class WakuContentTopicError(WakuClientError):
    def __init__(self, msg: str):
        """
        Raised when there is an error subscribing to a topic.

        Args:
            msg (str): The exception message.
        """

        super().__init__(msg)

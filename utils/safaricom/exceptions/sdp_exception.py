
class SDPException(Exception):
    """
    Custom exception class for Safaricom SDP integration.
    """

    def __init__(self, message, code=0, previous=None):
        """
        SDPException constructor.

        :param message: Exception message
        :param code: Optional error code
        :param previous: Optional previous exception for chaining
        """
        super().__init__(message)
        self.code = code
        self.previous = previous

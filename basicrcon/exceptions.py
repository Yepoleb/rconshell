class BrokenMessageError(Exception):
    pass

class BufferExhaustedError(BrokenMessageError):
    pass

class AuthenticationError(Exception):
    pass

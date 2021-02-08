class UnauthorizedError(Exception):
    def __init__(self):
        super().__init__('invalid token received')


class ExpiredTokenError(Exception):
    def __init__(self):
        super().__init__('the token has been expired')


class InvalidTokenError(Exception):
    def __init__(self):
        super().__init__('the token might have been manipulated')


class UnixTimeNeededError(Exception):
    def __init__(self):
        super().__init__("unix time parameters needed")


class TimeReversed(Exception):
    def __init__(self):
        super().__init__("TO cannot be set to the past of FROM")

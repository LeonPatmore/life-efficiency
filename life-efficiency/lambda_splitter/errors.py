class HTTPAwareException(Exception):

    def __init__(self,
                 status_code: int = 500,
                 error_message: str = None,
                 root_cause: Exception = None):
        self.root_cause = root_cause
        self.status_code = status_code
        self.error_message = error_message

    def get_body(self):
        if self.error_message:
            return {'error': self.error_message}
        elif self.root_cause:
            return {'error': 'exception during request processing',
                    'exception': self.root_cause}
        else:
            return {}

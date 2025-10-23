"""Domain-specific exceptions for the service layer.

Routers translate these into HTTP responses.
"""
class NotFoundError(Exception):
    def __init__(self, entity: str, identifier):
        super().__init__(f"{entity} with identifier '{identifier}' not found")
        self.entity = entity
        self.identifier = identifier

class ValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

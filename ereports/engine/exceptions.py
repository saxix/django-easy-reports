from django.core.exceptions import ValidationError


class FilterDefinitionError(ValidationError):
    def __init__(self, message, code=None, params=None):
        self.message = message
        super(FilterDefinitionError, self).__init__(message, code, params)

    def __str__(self):
        return str(self.message)

    def __repr__(self):
        return str(self.message)


class ColumnDefinitionError(ValidationError):
    pass


class OrderDefinitionError(ValidationError):
    pass


class GroupDefinitionError(ValidationError):
    pass

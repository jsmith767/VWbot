from EmberEventBot.constants import UserAccessLevel


class EventIdError(Exception):
    """Inapropriate event ID"""
    pass


class EmberAccessException(Exception):
    """Inappropriate command access"""

    def __init__(self, requested_access: UserAccessLevel, valid_access: UserAccessLevel):
        self.requested_access = requested_access
        self.valid_access = valid_access

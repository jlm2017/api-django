from django.db import IntegrityError
from django.db.models import Exists, OuterRef
from django.utils.functional import cached_property
from glom import glom, T, Coalesce

from agir.authentication.models import Role
from agir.notifications.models import Announcement


def add_announcements(person):
    pass


def get_notifications(request):
    if request.user.is_anonymous or request.user.type == Role.CLIENT_ROLE:
        return []

    person = request.user.person
    add_announcements(person)

    notifications = []

    return serialize_notifications(notifications)


def serialize_notifications(notifications):
    # All fields are either
    spec = [
        {
            "id": "id",
            "status": "status",
            "content": Coalesce(
                T.html_content(), T.announcement.html_content(), skip="", default=""
            ),
            "icon": Coalesce("icon", "announcement.icon", skip="", default=""),
            "link": Coalesce("link", "announcement.link", skip="", default=""),
            "created": (Coalesce("announcement.start_date", "created"), T.isoformat()),
        }
    ]

    return glom(notifications, spec)


class NotificationRequestManager:
    def __init__(self, request):
        self.request = request

    @cached_property
    def notifications(self):
        return get_notifications(self.request)

    def __iter__(self):
        return iter(self.notifications)

    def unread(self):
        return sum(not n.seen for n in self.notifications)


def add_notification(**kwargs):
    pass

import reversion
from django.contrib.gis.db.models.functions import Distance
from django.db import transaction
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse_lazy, reverse
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
    DestroyAPIView,
    CreateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from agir.events.models import Event
from agir.events.serializers import EventSerializer
from agir.groups.actions.notifications import (
    new_message_notifications,
    new_comment_notifications,
    someone_joined_notification,
)
from agir.groups.filters import GroupAPIFilterSet
from agir.groups.models import SupportGroup, SupportGroupSubtype, Membership
from agir.groups.serializers import (
    SupportGroupLegacySerializer,
    SupportGroupSubtypeSerializer,
    SupportGroupSerializer,
    SupportGroupDetailSerializer,
)
from agir.lib.pagination import APIPaginator
from agir.groups.tasks import send_message_notification_email

__all__ = [
    "GroupSearchAPIView",
    "GroupSubtypesView",
    "UserGroupsView",
    "GroupDetailAPIView",
    "NearGroupsAPIView",
    "GroupEventsAPIView",
    "GroupPastEventsAPIView",
    "GroupUpcomingEventsAPIView",
    "GroupPastEventReportsAPIView",
    "GroupMessagesAPIView",
    "GroupSingleMessageAPIView",
    "GroupMessageCommentsAPIView",
    "GroupSingleCommentAPIView",
    "GroupJoinAPIView",
]

from agir.lib.rest_framework_permissions import GlobalOrObjectPermissions
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment

from agir.msgs.serializers import (
    SupportGroupMessageSerializer,
    MessageCommentSerializer,
)


class GroupSearchAPIView(ListAPIView):
    "Vieille API encore utilisée par le composant js groupSelector du formulaire de dons"

    queryset = SupportGroup.objects.active()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupAPIFilterSet
    serializer_class = SupportGroupLegacySerializer
    pagination_class = APIPaginator
    permission_classes = (IsAuthenticated,)


class GroupSubtypesView(ListAPIView):
    serializer_class = SupportGroupSubtypeSerializer
    queryset = SupportGroupSubtype.objects.filter(
        visibility=SupportGroupSubtype.VISIBILITY_ALL
    )


class UserGroupsView(ListAPIView):
    serializer_class = SupportGroupSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        person = self.request.user.person
        person_groups = (
            SupportGroup.objects.filter(memberships__person=self.request.user.person)
            .active()
            .annotate(membership_type=F("memberships__membership_type"))
            .order_by("-membership_type", "name")
        )
        if person_groups.count() == 0 and person.coordinates is not None:
            person_groups = SupportGroup.objects.active()
            if person.is_2022_only:
                person_groups = person_groups.is_2022()
            person_groups = person_groups.annotate(
                distance=Distance("coordinates", person.coordinates)
            ).order_by("distance")[:3]
            for group in person_groups:
                group.membership = None

        return person_groups


class GroupDetailAPIView(RetrieveAPIView):
    permission_ = ("groups.view_supportgroup",)
    serializer_class = SupportGroupDetailSerializer
    queryset = SupportGroup.objects.active()


class NearGroupsAPIView(ListAPIView):
    serializer_class = SupportGroupDetailSerializer
    queryset = SupportGroup.objects.active()

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args, fields=["id", "name", "iconConfiguration", "location",], **kwargs
        )

    def get_queryset(self):
        if self.supportgroup.coordinates is None:
            return SupportGroup.objects.none()

        groups = (
            SupportGroup.objects.active()
            .exclude(pk=self.supportgroup.pk)
            .exclude(coordinates__isnull=True)
        )

        if self.supportgroup.is_2022:
            groups = groups.is_2022()

        groups = groups.annotate(
            distance=Distance("coordinates", self.supportgroup.coordinates)
        ).order_by("distance")

        return groups[:3]

    def dispatch(self, request, pk, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.active().get(pk=pk)
        except SupportGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)


class GroupEventsAPIView(ListAPIView):
    permission_ = ("groups.view_supportgroup",)
    serializer_class = EventSerializer
    queryset = Event.objects.listed()

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .distinct()
            .order_by("-start_time")
        )
        return events

    def dispatch(self, request, pk, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.get(pk=pk)
        except SupportGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)


class GroupUpcomingEventsAPIView(ListAPIView):
    permission_ = ("groups.view_supportgroup",)
    serializer_class = EventSerializer
    queryset = Event.objects.listed().upcoming()

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .upcoming()
            .distinct()
            .order_by("start_time")
        )
        return events

    def dispatch(self, request, pk, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.get(pk=pk)
        except SupportGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)


class GroupPastEventsAPIView(ListAPIView):
    permission_ = ("groups.view_supportgroup",)
    serializer_class = EventSerializer
    queryset = Event.objects.listed().past()
    pagination_class = APIPaginator

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .past()
            .distinct()
            .order_by("-start_time")
        )
        return events

    def dispatch(self, request, pk, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.get(pk=pk)
        except SupportGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)


class GroupPastEventReportsAPIView(ListAPIView):
    permission_ = ("groups.view_supportgroup",)
    serializer_class = EventSerializer
    queryset = Event.objects.listed().past()

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .past()
            .exclude(report_content="")
            .distinct()
            .order_by("-start_time")
        )
        return events

    def dispatch(self, request, pk, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.get(pk=pk)
        except SupportGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)


class GroupMessagesPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "POST": []}
    object_perms_map = {
        "GET": ["msgs.view_supportgroupmessage"],
        "POST": ["msgs.add_supportgroupmessage"],
    }


class GroupMessagesAPIView(ListCreateAPIView):
    serializer_class = SupportGroupMessageSerializer
    permission_classes = (GroupMessagesPermissions,)
    pagination_class = APIPaginator

    def initial(self, request, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.get(pk=kwargs["pk"])
        except SupportGroup.DoesNotExist:
            raise NotFound()

        self.check_object_permissions(request, self.supportgroup)

        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return self.supportgroup.messages.filter(deleted=False).order_by("-created")

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args, fields=self.serializer_class.LIST_FIELDS, **kwargs
        )

    def perform_create(self, serializer):
        with transaction.atomic():
            message = serializer.save(
                author=self.request.user.person, supportgroup=self.supportgroup
            )
            new_message_notifications(message)


class GroupSingleMessageAPIView(RetrieveUpdateDestroyAPIView):
    queryset = SupportGroupMessage.objects.filter(deleted=False)
    serializer_class = SupportGroupMessageSerializer
    permission_classes = (GlobalOrObjectPermissions,)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args, fields=self.serializer_class.DETAIL_FIELDS, **kwargs
        )

    def perform_update(self, serializer):
        with reversion.create_revision():
            super().perform_update(serializer)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()


class GroupMessageCommentsPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "POST": []}
    object_perms_map = {
        "GET": ["msgs.view_supportgroupmessage"],
        "POST": ["msgs.add_supportgroupmessagecomment"],
    }


class GroupMessageCommentsAPIView(ListCreateAPIView):
    serializer_class = MessageCommentSerializer
    permission_classes = (GroupMessageCommentsPermissions,)

    def initial(self, request, *args, **kwargs):
        try:
            self.message = SupportGroupMessage.objects.get(pk=kwargs["pk"])
        except SupportGroupMessage.DoesNotExist:
            raise NotFound()

        self.check_object_permissions(request, self.message)

        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return self.message.comments.filter(deleted=False)

    def perform_create(self, serializer):
        with transaction.atomic():
            comment = serializer.save(
                author=self.request.user.person, message=self.message
            )
            new_comment_notifications(comment)


class GroupSingleCommentAPIView(UpdateAPIView, DestroyAPIView):
    queryset = SupportGroupMessageComment.objects.filter(deleted=False)
    serializer_class = MessageCommentSerializer
    permission_classes = (GlobalOrObjectPermissions,)

    def perform_update(self, serializer):
        with reversion.create_revision():
            super().perform_update(serializer)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()


class GroupJoinAPIView(CreateAPIView):
    queryset = SupportGroup.objects.active()
    permission_ = ("groups.view_supportgroup",)

    def initial(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.check_object_permissions(request, self.object)

        super().initial(request, *args, **kwargs)

    def check_permissions(self, request):
        if not request.user.is_authenticated or request.user.person is None:
            raise PermissionDenied(
                detail={
                    "redirectTo": f'{reverse_lazy("short_code_login")}?next={reverse("view_group", kwargs={"pk": self.object.pk})}'
                },
            )
        if self.object.is_2022 and not request.user.person.is_2022:
            raise PermissionDenied(detail={"redirectTo": f'{reverse("join")}?type=2'},)
        if not self.object.is_2022 and not request.user.person.is_insoumise:
            raise PermissionDenied(detail={"redirectTo": f'{reverse("join")}?type=I'},)
        if self.object.is_full:
            raise PermissionDenied(
                detail={
                    "redirectTo": reverse("full_group", kwargs={"pk": self.object.pk})
                }
            )
        if Membership.objects.filter(
            person=request.user.person, supportgroup=self.object
        ).exists():
            raise PermissionDenied(
                detail={
                    "redirectTo": reverse("view_group", kwargs={"pk": self.object.pk})
                },
            )

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            membership = Membership.objects.create(
                supportgroup=self.object, person=request.user.person
            )
            someone_joined_notification(
                membership, membership_count=self.object.members_count
            )
            return Response(status=status.HTTP_201_CREATED)

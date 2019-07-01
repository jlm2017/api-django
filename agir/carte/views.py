import json
from datetime import timedelta

import django_filters
from django.contrib.gis.geos import Polygon
from django.db.models import Q, Count
from django.http import QueryDict, Http404
from django.utils.html import mark_safe
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.decorators import cache
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView, DetailView
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView

from agir.lib.export import dict_to_camelcase
from . import serializers
from ..events.models import Event, EventSubtype
from ..groups.models import SupportGroup, SupportGroupSubtype


def parse_bounds(bounds):
    if not bounds:
        return None

    try:
        bbox = json.loads(bounds)
    except json.JSONDecodeError:
        return None

    if not len(bbox) == 4:
        return None

    try:
        bbox = [float(c) for c in bbox]
    except ValueError:
        return None

    if not (-180.0 <= bbox[0] < bbox[2] <= 180.0) or not (
        -90.0 <= bbox[1] < bbox[3] <= 90
    ):
        return None

    return bbox


class BBoxFilterBackend(object):
    error_message = _(
        "Le paramètre bbox devrait être un tableau de 4 flottants [lon1, lat1, lon2, lat2]."
    )

    def filter_queryset(self, request, queryset, view):
        if not "bbox" in request.query_params:
            return queryset

        bbox = request.query_params["bbox"]

        if bbox is None:
            raise ValidationError(self.error_message)

        bbox = Polygon.from_bbox(bbox)

        return queryset.filter(coordinates__intersects=bbox)


class FixedModelMultipleChoiceFilter(django_filters.ModelMultipleChoiceFilter):
    def get_filter_predicate(self, v):
        return {self.field_name: v}


class EventFilterSet(django_filters.rest_framework.FilterSet):
    subtype = FixedModelMultipleChoiceFilter(
        field_name="subtype", to_field_name="label", queryset=EventSubtype.objects.all()
    )
    include_past = django_filters.BooleanFilter(
        "start_time",
        label="Inclure les événements passés",
        method="filter_include_past",
    )
    include_hidden = django_filters.BooleanFilter(
        label="Include les événements non publiés", method="filter_include_hidden"
    )

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            data = data.copy()
            if data.get("include_past") is None:
                data["include_past"] = False
            if data.get("include_hidden") is None:
                data["include_hidden"] = False

        super().__init__(data, *args, **kwargs)

    @property
    def qs(self):
        return super().qs[:5000]

    def filter_include_past(self, queryset, name, value):
        if not value:
            return queryset.upcoming(published_only=False)
        else:
            return queryset

    def filter_include_hidden(self, qs, name, value):
        if not value:
            return qs.listed()
        else:
            return qs

    class Meta:
        model = Event
        fields = ("subtype", "include_past")


class EventsView(ListAPIView):
    serializer_class = serializers.MapEventSerializer
    filter_backends = (BBoxFilterBackend, DjangoFilterBackend)
    filterset_class = EventFilterSet
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        qs = Event.objects.all()
        if self.request.user is None or not self.request.user.has_perms(
            "view_hidden_event"
        ):
            qs = qs.listed()
        return qs.filter(coordinates__isnull=False).select_related("subtype")

    @cache.cache_control(max_age=300, public=True)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GroupFilterSet(django_filters.rest_framework.FilterSet):
    subtype = FixedModelMultipleChoiceFilter(
        field_name="subtypes",
        to_field_name="label",
        queryset=SupportGroupSubtype.objects.all(),
    )

    class Meta:
        model = SupportGroup
        fields = ("subtype",)


class GroupsView(ListAPIView):
    serializer_class = serializers.MapGroupSerializer
    filter_backends = (BBoxFilterBackend, DjangoFilterBackend)
    filterset_class = GroupFilterSet
    queryset = (
        SupportGroup.objects.active()
        .filter(coordinates__isnull=False)
        .prefetch_related("subtypes")
    )
    authentication_classes = []

    @cache.cache_control(max_age=300, public=True)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            SupportGroup.objects.active()
            .filter(coordinates__isnull=False)
            .prefetch_related("subtypes")
            .annotate(
                current_events_count=Count(
                    "organized_events",
                    filter=Q(
                        organized_events__start_time__range=(
                            now() - timedelta(days=62),
                            now() + timedelta(days=31),
                        ),
                        organized_events__visibility=Event.VISIBILITY_PUBLIC,
                    ),
                )
            )
        )


class MapViewMixin:
    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @classmethod
    def get_type_information(cls, id, label):
        return {"id": id, "label": label}


class AbstractListMapView(MapViewMixin, TemplateView):
    subtype_model = None

    def get_context_data(self, **kwargs):
        subtypes = self.subtype_model.objects.all()

        params = QueryDict(mutable=True)

        subtype_label = self.request.GET.getlist("subtype")
        if subtype_label:
            subtypes = subtypes.filter(label__in=subtype_label)
            params.setlist("subtype", subtype_label)

        if self.request.GET.get("include_past"):
            params["include_past"] = "1"

        if self.request.GET.get("include_hidden"):
            params["include_hidden"] = "1"

        subtype_info = [
            dict_to_camelcase(st.get_subtype_information()) for st in subtypes
        ]
        types = self.subtype_model._meta.get_field("type").choices
        type_info = [
            dict_to_camelcase(self.get_type_information(id, str(label)))
            for id, label in types
        ]

        bounds = parse_bounds(self.request.GET.get("bounds"))

        querystring = ("?" + params.urlencode()) if params else ""

        return super().get_context_data(
            type_config=type_info,
            subtype_config=subtype_info,
            bounds=bounds,
            querystring=mark_safe(querystring),
            **kwargs
        )


class AbstractSingleItemMapView(MapViewMixin, DetailView):
    def get_context_data(self, **kwargs):
        if self.object.coordinates is None:
            raise Http404()

        subtype = self.get_subtype()
        icon_config = dict_to_camelcase(subtype.get_subtype_information())

        return super().get_context_data(
            subtype_config=icon_config,
            coordinates=self.object.coordinates.coords,
            **kwargs
        )


class EventMapMixin:
    subtype_model = EventSubtype
    queryset = Event.objects.listed()

    def get_subtype(self):
        return self.object.subtype


class GroupMapMixin:
    subtype_model = SupportGroupSubtype
    queryset = SupportGroup.objects.active()
    context_object_name = "group"

    def get_subtype(self):
        return self.object.subtypes.first()


class EventMapView(EventMapMixin, AbstractListMapView):
    template_name = "carte/events.html"


class GroupMapView(GroupMapMixin, AbstractListMapView):
    template_name = "carte/groups.html"


class SingleEventMapView(EventMapMixin, AbstractSingleItemMapView):
    template_name = "carte/single_event.html"
    queryset = Event.objects.all()

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm("events.view_event", self.get_object()):
            raise Http404("Cette page n'existe pas.")
        return super().get(request, *args, **kwargs)


class SingleGroupMapView(GroupMapMixin, AbstractSingleItemMapView):
    template_name = "carte/single_group.html"

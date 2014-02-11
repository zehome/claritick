from rest_framework import generics, filters
from ticket.serializers import (
    TicketListSerializer,
    StateSerializer,
    PrioritySerializer
)
from ticket.models import Ticket, State, Priority


class StateListView(generics.ListAPIView):
    serializer_class = StateSerializer
    model = State


class PriorityListView(generics.ListAPIView):
    serializer_class = PrioritySerializer
    model = Priority


class TicketListView(generics.ListAPIView):
    serializer_class = TicketListSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    # TODO: handle tags
    search_fields = ('@title', '@text')
    ordering = ('id', 'date_open', 'date_close', 'last_modification')
    paginate_by = 50
    paginate_by_param = None
    max_paginate_by = 100

    def get_queryset(self):
        qs = Ticket.objects.foruser(self.request.user)
        qs = qs.select_related("priority__label", "state__label")
        return qs

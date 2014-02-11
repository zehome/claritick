from rest_framework import serializers
from ticket.models import Ticket, State, Priority


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State


class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority


class TicketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('id', 'date_open', 'last_modification', 'date_close',
                  'title', 'state', 'priority', 'customer')

    state = serializers.PrimaryKeyRelatedField()
    priority = serializers.PrimaryKeyRelatedField()
    customer = serializers.PrimaryKeyRelatedField()

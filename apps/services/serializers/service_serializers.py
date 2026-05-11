from rest_framework import serializers
from ..models import Component, Vehicle, ServiceOrder, Issue
from apps.services.constants.enums import OrderStatus

class ComponentSerializer(serializers.ModelSerializer):
    """Handles parts and their two-tier pricing."""
    class Meta:
        model = Component
        fields = ['id', 'name', 'repair_price', 'purchase_price']

class VehicleSerializer(serializers.ModelSerializer):
    """Handles vehicle registration."""
    class Meta:
        model = Vehicle
        fields = ['id', 'vin', 'make', 'model', 'owner_name', 'contact_number']

class IssueSerializer(serializers.ModelSerializer):
    """
    Handles specific repairs. 
    Includes component_name for easy display on the frontend.
    """
    component_name = serializers.ReadOnlyField(source='component.name')
    
    class Meta:
        model = Issue
        fields = [
            'id', 'service_order', 'component', 'component_name', 
            'issue_type', 'price'
        ]
        # Price is read-only because the model.save() logic sets it
        read_only_fields = ['price']


    def validate(self, data):
        # 1. THE "EDIT" CHECK (Updating an existing part)
        # If self.instance exists, we are editing. Check the DB status.
        if self.instance and self.instance.service_order.status == OrderStatus.PAID:
            raise serializers.ValidationError("This order is PAID. You cannot edit its parts.")

        # 2. THE "NEW" CHECK (Adding a part to an order)
        # Check the status of the order provided in the request.
        service_order = data.get('service_order')
        if service_order and service_order.status == OrderStatus.PAID:
            raise serializers.ValidationError("This order is PAID. You cannot add new parts to it.")

        return data

class ServiceOrderSerializer(serializers.ModelSerializer):
    """
    The main 'Ticket' serializer. 
    Nest the issues so React can show the full bill in one request.
    """
    issues = IssueSerializer(many=True, read_only=True)
    vehicle_info = serializers.SerializerMethodField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = ServiceOrder
        fields = [
            'id', 'vehicle', 'vehicle_info', 'description', 
            'status', 'created_at', 'issues', 'total_price'
        ]
        
        read_only_fields = ['status']

    def get_vehicle_info(self, obj):
        # Returns a nice string like 'Toyota Camry (VIN123...)'
        return f"{obj.vehicle.make} {obj.vehicle.model} ({obj.vehicle.vin})"
    
    def validate(self, data):
        """
        Validation Logic:
        1. If the order is already 'paid', block ALL incoming data changes.
        """
        # self.instance represents the object already in the database
        if self.instance and self.instance.status == OrderStatus.PAID:
            raise serializers.ValidationError({
                "order_locked": "This order is finalized and PAID. No further modifications are allowed to the description or vehicle details."
            })

        return data
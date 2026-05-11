from rest_framework import serializers
from apps.services.constants.enums import PeriodChoice

class RevenueQuerySerializer(serializers.Serializer):
    period = serializers.ChoiceField(choices=PeriodChoice.choices, default=PeriodChoice.DAILY)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate(self, data):
        from_d = data.get('from_date')
        to_d = data.get('to_date')
        period = data.get('period', PeriodChoice.DAILY)

        # 1. Logic check: Ensure "from" isn't after "to"
        if from_d and to_d:
            if from_d > to_d:
                raise serializers.ValidationError({
                    "from_date": "The start date cannot be later than the end date."
                })

        # 2. Guardrail: Prevent data-overload on the frontend
        if from_d and to_d and period == PeriodChoice.DAILY:
            delta = to_d - from_d
            if delta.days > 90:
                raise serializers.ValidationError({
                    "period": "Daily view is limited to a 90-day range to keep the chart readable. Please select a shorter range or switch to 'monthly' view."
                })
        
        return data

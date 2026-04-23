from rest_framework import serializers
from .models import Habit

class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at', 'last_reminded')

    def validate(self, data):
        # 1. Нельзя одновременно указать связанную привычку и вознаграждение
        if data.get('related_habit') and data.get('reward'):
            raise serializers.ValidationError(
                "Нельзя одновременно выбрать связанную привычку и указать вознаграждение."
            )

        # 2. Время выполнения не более 120 секунд
        if data.get('duration', 0) > 120:
            raise serializers.ValidationError("Время выполнения не может быть больше 120 секунд.")

        # 3. Связанная привычка должна быть приятной
        related = data.get('related_habit')
        if related and not related.is_pleasant:
            raise serializers.ValidationError("Связанная привычка должна быть приятной.")

        # 4. У приятной привычки не может быть вознаграждения или связанной привычки
        if data.get('is_pleasant'):
            if data.get('reward') or data.get('related_habit'):
                raise serializers.ValidationError(
                    "У приятной привычки не может быть вознаграждения или связанной привычки."
                )

        # 5. Периодичность от 1 до 7 дней
        period = data.get('periodicity', 1)
        if period < 1 or period > 7:
            raise serializers.ValidationError("Периодичность должна быть от 1 до 7 дней.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

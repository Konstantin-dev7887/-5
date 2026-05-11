from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwner


class HabitListCreateView(generics.ListCreateAPIView):
    """
    GET: список привычек текущего пользователя (с пагинацией).
    POST: создание новой привычки.
    """
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: просмотр одной привычки.
    PUT/PATCH: редактирование.
    DELETE: удаление.
    """
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Habit.objects.all()


class PublicHabitListView(generics.ListAPIView):
    """
    GET: список публичных привычек (доступно всем).
    """
    serializer_class = HabitSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)

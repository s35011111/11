from django.db.models import Q
# Create your views here.
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Habit
from .pagination import StandardPagePagination
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (UserProfileSerializer,
                          UserListSerializer,
                          UserRegistrationSerializer,
                          HabitSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):

        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['list', 'retrieve']:
            return UserListSerializer
        return UserProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return CustomUser.objects.all()
        if user.is_authenticated:
            return CustomUser.objects.filter(username=self.request.user)
        else:
            return Habit.objects.none()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = StandardPagePagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdminOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Habit.objects.all()
        if user.is_authenticated:
            return Habit.objects.filter(Q(is_public=True) | Q(user=user))
        return Habit.objects.filter(is_public=True)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

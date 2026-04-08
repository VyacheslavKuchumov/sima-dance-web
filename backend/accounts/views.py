from django.db.models import Case, Count, IntegerField, Q, Value, When
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from app.permissions import IsSuperUser
from .serializers import (
    AdminUserSerializer,
    AdminUserImpersonationSerializer,
    SignupGroupSerializer,
    UserSerializer,
    UserSignupSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)
from .group_defaults import DEFAULT_SIGNUP_GROUP_NAMES
from .models import UserGroup

User = get_user_model()


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])

        return Response(
            {'detail': 'Пароль успешно обновлен.'},
            status=status.HTTP_200_OK,
        )


class SignupView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"id": user.id, "username": user.username},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupGroupsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        custom_order = Case(
            *[
                When(name=name, then=Value(index))
                for index, name in enumerate(DEFAULT_SIGNUP_GROUP_NAMES)
            ],
            default=Value(len(DEFAULT_SIGNUP_GROUP_NAMES)),
            output_field=IntegerField(),
        )
        groups = UserGroup.objects.annotate(signup_order=custom_order).order_by("signup_order", "name")
        serializer = SignupGroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminUsersListView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        search = (request.query_params.get('search') or '').strip()
        users = User.objects.select_related('profile__group').annotate(
            bookings_count=Count('bookings', distinct=True),
        )

        if search:
            users = users.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(profile__full_name__icontains=search)
                | Q(profile__child_full_name__icontains=search)
                | Q(profile__group__name__icontains=search)
            )

        serializer = AdminUserSerializer(
            users.order_by('-is_superuser', 'username', 'id'),
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminUserImpersonationView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request):
        serializer = AdminUserImpersonationSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        target_user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(target_user)
        refresh['impersonation'] = True
        refresh['impersonated_by'] = request.user.id

        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(target_user).data,
            },
            status=status.HTTP_200_OK,
        )

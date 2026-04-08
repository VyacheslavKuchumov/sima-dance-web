from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import UserGroup, UserProfile

User = get_user_model()


class SignupGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ["id", "name"]


class UserProfileSerializer(serializers.ModelSerializer):
    group = SignupGroupSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["group", "full_name", "child_full_name"]


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'profile',
        ]

    def get_profile(self, obj):
        try:
            profile = obj.profile
        except UserProfile.DoesNotExist:
            return None
        return UserProfileSerializer(profile).data


class AdminUserSerializer(UserSerializer):
    bookings_count = serializers.IntegerField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['date_joined', 'last_login', 'bookings_count']


class AdminUserImpersonationSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
    )

    def validate_user_id(self, value):
        request = self.context.get('request')

        if request and value.pk == request.user.pk:
            raise serializers.ValidationError('Вы уже авторизованы под этим пользователем.')

        if not value.is_active:
            raise serializers.ValidationError('Нельзя войти под неактивным пользователем.')

        return value


class AdminUserPasswordResetSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
    )


class UserUpdateSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=UserGroup.objects.all(), required=False)
    full_name = serializers.CharField(max_length=255, required=False)
    child_full_name = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'group', 'full_name', 'child_full_name']

    def update(self, instance, validated_data):
        group = validated_data.pop("group", serializers.empty)
        full_name = validated_data.pop("full_name", serializers.empty)
        child_full_name = validated_data.pop("child_full_name", serializers.empty)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        with transaction.atomic():
            if validated_data:
                instance.save()

            has_profile_updates = any(
                value is not serializers.empty
                for value in (group, full_name, child_full_name)
            )
            if not has_profile_updates:
                return instance

            try:
                profile = instance.profile
            except UserProfile.DoesNotExist:
                if group is serializers.empty:
                    raise serializers.ValidationError({
                        "group": "Нужно выбрать группу для создания профиля."
                    })

                profile = UserProfile.objects.create(
                    user=instance,
                    group=group,
                    full_name="" if full_name is serializers.empty else full_name,
                    child_full_name="" if child_full_name is serializers.empty else child_full_name,
                )
                instance.profile = profile
                return instance

            if group is not serializers.empty:
                profile.group = group
            if full_name is not serializers.empty:
                profile.full_name = full_name
            if child_full_name is not serializers.empty:
                profile.child_full_name = child_full_name
            profile.save()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Текущий пароль введен неверно.')
        return value

    def validate_new_password(self, value):
        user = self.context['request'].user
        validate_password(value, user=user)
        return value


class UserSignupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=UserGroup.objects.all())
    full_name = serializers.CharField(max_length=255)
    child_full_name = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'group', 'full_name', 'child_full_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        group = validated_data.pop("group")
        full_name = validated_data.pop("full_name")
        child_full_name = validated_data.pop("child_full_name")
        password = validated_data.pop("password")

        with transaction.atomic():
            user = User.objects.create_user(password=password, **validated_data)
            UserProfile.objects.create(
                user=user,
                group=group,
                full_name=full_name,
                child_full_name=child_full_name,
            )

        return user

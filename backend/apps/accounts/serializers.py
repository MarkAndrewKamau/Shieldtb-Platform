from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class DetailSerializer(serializers.Serializer):
    detail = serializers.CharField()


class ShieldTBTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        if user.facility_id:
            token["facility_id"] = str(user.facility_id)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12, required=False)
    facility_id = serializers.IntegerField(source="facility.id", read_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "facility",
            "facility_id",
            "phone",
            "is_active",
            "must_reset_password",
            "password",
        ]
        read_only_fields = ["id", "facility_id"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            user.must_reset_password = True
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
            instance.must_reset_password = False
        instance.save()
        return instance


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "facility",
            "phone",
            "password",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "facility": {"required": True},
        }

    def validate_role(self, value):
        if value == self.Meta.model.Role.ADMIN:
            raise serializers.ValidationError("Admin accounts cannot be created via public signup.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.must_reset_password = False
        user.save()
        return user


class UserEnvelopeSerializer(serializers.Serializer):
    user = UserSerializer()

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class DriverRegisterSerializer(serializers.ModelSerializer):
    """
    Public self-registration — drivers only.

    Role is never taken from client input. It is hardcoded to DRIVER in
    create(), so this endpoint can never be used to create staff accounts.
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            role=User.Role.DRIVER,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Read-only representation of the logged-in user, used in auth responses."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]
        read_only_fields = fields
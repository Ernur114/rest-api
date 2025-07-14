from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from users.models import Client


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "pk",
            "username",
            "first_name",
            "last_name",
            "avatar",
        ]


class UserModelSerializer(serializers.ModelSerializer):
    join_friends = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, required=False
    )
    remove_friends = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, required=False
    )
    friends = FriendSerializer(many=True, read_only=True)
    class Meta:
        model = Client
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "avatar",
            "friends",
            "join_friends",
            "remove_friends",
        ]

    def validate_username(self, value):
        if "admin" in value.lower():
            raise serializers.ValidationError(
                "Username cannot contain 'admin'"
            )
        return value

    def validate(self, attrs):
        if attrs["username"] == attrs.get("password"):
            raise serializers.ValidationError(
                "Password cannot be the same as username"
            )
        self.validate_username(value=attrs["username"])
        return attrs

    def create(self, validated_data: dict) -> Client:
        validated_data["password"] = make_password(
            validated_data["password"]
        )
        validated_data.pop("friends", [])
        validated_data.pop("join_friends", [])
        validated_data.pop("remove_friends", [])
        return super().create(validated_data)

    def update(self, instance: Client, validated_data: dict):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"]
            )
        join_friends = validated_data.pop("join_friends", [])
        remove_friends = validated_data.pop("remove_friends", [])
        if join_friends:
            instance.friends.add(*join_friends)
        if remove_friends:
            instance.friends.remove(*remove_friends)
        return super().update(instance, validated_data)

__all__ = ("RedirectCreateSerializer", "RedirectSerializer")

from typing import Any

from rest_framework import serializers

from redirects.models import Redirect


class RedirectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redirect
        fields = (
            Redirect.id.field.name,
            Redirect.long_link.field.name,
            Redirect.short_link.field.name,
            Redirect.password.field.name,
            Redirect.validity_days.field.name,
            Redirect.validity_clicks.field.name,
            Redirect.created_at.field.name,
            Redirect.updated_at.field.name,
            Redirect.create_method.field.name,
            Redirect.is_active.field.name,
            Redirect.deactivated_at.field.name,
        )


class RedirectCreateSerializer(serializers.Serializer):
    long_link = serializers.URLField(
        required=True,
        max_length=Redirect.long_link.field.max_length,
    )
    short_link = serializers.CharField(
        required=False,
        max_length=Redirect.short_link.field.max_length,
    )
    password = serializers.CharField(
        required=False,
        max_length=Redirect.password.field.max_length,
    )
    validity_days = serializers.IntegerField(
        required=False,
        default=Redirect.validity_days.field.default,
    )
    validity_clicks = serializers.IntegerField(
        required=False,
        default=None,
    )

    def create(self, validated_data: dict[str, Any]) -> Redirect:
        return Redirect.objects.create(**validated_data)

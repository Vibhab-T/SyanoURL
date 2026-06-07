import re
from datetime import timedelta
from django.utils import timezone

from rest_framework import serializers

from .models import Click, ShortURL

CUSTOM_CODE_REGEXP = re.compile(r'^[a-zA-Z0-9]+$')

class ClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Click
        fields = ("id", "clicked_at")
    

class ShortURLSerializer(serializers.ModelSerializer):
    click_count = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    og_url = serializers.URLField(max_length=2048) #write only

    #optional fields to create
    custom_code = serializers.CharField(max_length=50, min_length=3, required=False, allow_blank=True, write_only=True)
    expires_at = serializers.DateTimeField(required=False, default=None, allow_null=True)

    class Meta:
        model = ShortURL
        fields = ("id", "og_url", "short_code", "is_custom", "expires_at", "created_at", "click_count", 
                  "is_expired", "custom_code")
        read_only_fields = ("id", "short_code", "is_custom", "created_at","click_count", "is_expired")

    def validate_custom_code(self, value):
        if not value:
            return value
        if not CUSTOM_CODE_REGEXP.match(value):
            raise serializers.ValidationError("Custom code should only be alphanumeric. No special characters.")
        if ShortURL.objects.filter(short_code=value).exists():
            raise serializers.ValidationError("This custom code already exists, please try again")
        return value
    
    def validate_expires_at(self, value):
        if value is not None and value <= timezone.now():
            raise serializers.ValidationError("Expiry must be in the future")

class ShortURLDetailSerializer(ShortURLSerializer):
    #for the analytics view, includes the per click time stamp
    #basically just adding more detail the returned json

    clicks = ClickSerializer(many=True, read_only=True)
    
    class Meta(ShortURLSerializer.Meta):
        fields = ShortURLSerializer.Meta.fields + ("clicks", )
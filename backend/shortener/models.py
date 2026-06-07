from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


def default_expiry():
    return timezone.now() + timedelta(days=10)


class ShortURL(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="short_urls")
    og_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=20, unique=True, db_index=True)
    is_custom = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=default_expiry)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Short Code: {self.short_code} \n Original URL: {self.og_url}"
    
    @property
    def click_count(self):
        return self.clicks.count()
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

class Click(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE, related_name="clicks")
    clicked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-clicked_at"]
    
    def __str__(self):
        return f"Clicked on {self.short_url.short_code} at {self.clicked_at}"
    


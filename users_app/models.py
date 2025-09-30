from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    TYPE_CHOICES = (
        ("customer", "Customer"),
        ("business", "Business"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    first_name = models.CharField(max_length=150, blank=True, default="")
    last_name = models.CharField(max_length=150, blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    tel = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=255, blank=True, default="")
    file = models.ImageField(upload_to="profiles/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        return f"Profile({self.user.username}, {self.type})"

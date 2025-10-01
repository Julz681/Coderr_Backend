from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    """
    Model representing a review written by a customer for a business user.
    Includes rating, description, and timestamps.
    """
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="written_reviews")
    rating = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("business_user", "reviewer")
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return f"Review({self.id} -> {self.business_user.username} by {self.reviewer.username})"

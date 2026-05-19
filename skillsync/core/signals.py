from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, Review


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Review)
def refresh_reviewee_rating(sender, instance, **kwargs):
    summary = Review.objects.filter(reviewee=instance.reviewee).aggregate(
        average=Avg("rating"),
        total=Count("id"),
    )
    Profile.objects.filter(user=instance.reviewee).update(
        rating=round(summary["average"] or 0, 2),
        total_reviews=summary["total"],
    )

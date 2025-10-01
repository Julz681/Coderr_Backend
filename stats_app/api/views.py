from django.db.models import Avg, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from reviews_app.models import Review
from users_app.models import UserProfile
from offers_app.models import Offer


class BaseInfoView(APIView):
    """
    API view for retrieving basic application statistics:
    total reviews, average rating, number of business profiles, and offers.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        review_count = Review.objects.count()
        avg_rating = Review.objects.aggregate(a=Avg("rating"))["a"] or 0
        average_rating = round(float(avg_rating), 1)
        business_profile_count = UserProfile.objects.filter(type="business").count()
        offer_count = Offer.objects.count()
        return Response(
            {
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": business_profile_count,
                "offer_count": offer_count,
            }
        )

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg
from reviews_app.models import Review
from users_app.models import UserProfile
from offers_app.models import Offer

class BaseInfoView(APIView):
    def get(self, request):
        rc = Review.objects.count()
        avg = Review.objects.aggregate(a=Avg("rating"))["a"] or 0
        avg = round(float(avg), 1) if avg else 0
        bcount = UserProfile.objects.filter(type="business").count()
        ocount = Offer.objects.count()
        return Response({
            "review_count": rc,
            "average_rating": avg,
            "business_profile_count": bcount,
            "offer_count": ocount,
        })

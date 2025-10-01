from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """
    Custom pagination for offers.
    Defines default page size and limits for paginated API responses.
    """
    page_size = 6               # Default
    page_size_query_param = 'page_size'
    max_page_size = 100

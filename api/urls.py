from django.urls import include, path
from drfpasswordless.views import ObtainEmailCallbackToken
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, CommentViewSet, GenreViewSet, ObtainToken, ReviewViewSet,
    TitleViewSet, UserViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/token/', ObtainToken.as_view(), name='obtain_token'),
    path('v1/email/', ObtainEmailCallbackToken.as_view(), name='obtain_email'),
    path('v1/', include(router.urls))
]

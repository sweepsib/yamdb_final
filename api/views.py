from django.db.models import Avg
from django.shortcuts import get_object_or_404
from drfpasswordless.serializers import TokenResponseSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .filters import TitleFilter
from .models import Category, Genre, Review, Title, User
from .permissions import (
    IsAdminOrReadOnly, IsAuthorOrAdminOrModeratorOrReadOnly, IsAuthReadOnly,
    IsStaffOnly)
from .serializers import (
    CallbackTokenAuthSerializer, CategorySerializer, CommentSerializer,
    GenreSerializer, ReviewSerializer, TitleCreateUpdateSerializer,
    TitleListSerializer, UserProfileSerializer)
from .utils import get_tokens_for_user


class AbstractBaseObtainAuthToken(APIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        token = get_tokens_for_user(user)
        token_serializer = TokenResponseSerializer(data=token, partial=True)

        if token_serializer.is_valid():
            return Response(token, status=status.HTTP_200_OK)
        else:
            return Response(
                {'detail': 'Couldn"t log you in. Try again later.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ObtainToken(AbstractBaseObtainAuthToken):
    permission_classes = (AllowAny,)
    serializer_class = CallbackTokenAuthSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthReadOnly, IsStaffOnly,)
    queryset = User.objects.all()
    lookup_field = 'username'

    @action(detail=False, methods=['GET', 'PATCH'],
            permission_classes=(IsAuthReadOnly,))
    def me(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ListCreateDestroyViewSet(CreateModelMixin,
                               DestroyModelMixin,
                               ListModelMixin,
                               GenericViewSet):
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PageNumberPagination
    search_fields = ['name']
    filter_backends = [SearchFilter]
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(ModelViewSet):
    pagination_class = PageNumberPagination
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleListSerializer
        return TitleCreateUpdateSerializer

    def get_queryset(self):
        return Title.objects.annotate(
            rating=Avg('reviews__score')
        ).all().order_by('-id')


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = [
        IsAuthorOrAdminOrModeratorOrReadOnly, IsAuthenticatedOrReadOnly
    ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = [
        IsAuthorOrAdminOrModeratorOrReadOnly, IsAuthenticatedOrReadOnly
    ]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)

from django_filters import rest_framework as filters

from .models import Title


class TitleFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    year = filters.NumberFilter(field_name='year', lookup_expr='exact')
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='icontains'
    )
    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='icontains'
    )

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']

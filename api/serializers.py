from drfpasswordless.models import CallbackToken
from drfpasswordless.serializers import TokenField, token_age_validator
from drfpasswordless.settings import api_settings
from drfpasswordless.utils import verify_user_alias
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Category, Comment, Genre, Review, Title, User


class AbstractBaseCallbackTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    confirmation_code = TokenField(
        min_length=6,
        max_length=6,
        validators=[token_age_validator]
    )

    def validate_alias(self, attrs):
        email = attrs.get('email')
        if email:
            return 'email', email
        return None


class CallbackTokenAuthSerializer(AbstractBaseCallbackTokenSerializer):
    def validate(self, attrs):

        try:
            alias_type, alias = self.validate_alias(attrs)
            callback_token = attrs.get('confirmation_code')
            user = User.objects.get(**{alias_type + '__iexact': alias})
            token = CallbackToken.objects.get(
                **{
                    'user': user,
                    'key': callback_token,
                    'type': CallbackToken.TOKEN_TYPE_AUTH,
                    'is_active': True
                }
            )
            if token.user == user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg)
                if api_settings.PASSWORDLESS_USER_MARK_EMAIL_VERIFIED:
                    user = User.objects.get(pk=token.user.pk)
                    success = verify_user_alias(user, token)
                    if not success:
                        msg = 'Error validating user alias.'
                        raise serializers.ValidationError(msg)
                attrs['user'] = user
                return attrs
            else:
                msg = 'Invalid Token'
                raise serializers.ValidationError(msg)
        except CallbackToken.DoesNotExist:
            msg = 'Invalid alias parameters provided.'
            raise serializers.ValidationError(msg)
        except User.DoesNotExist:
            msg = 'Invalid user alias parameters provided.'
            raise serializers.ValidationError(msg)
        except ValidationError:
            msg = 'Invalid alias parameters provided.'
            raise serializers.ValidationError(msg)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'bio'
        )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id', )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id', )


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    def validate(self, data):
        if self.context['request'].method == 'POST':
            if Review.objects.filter(
                title=self.context['view'].kwargs.get('title_id'),
                author=self.context['request']._user,
            ).exists():
                raise serializers.ValidationError(
                    'You can write only one review to this title.'
                )
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = '__all__'
        model = Comment

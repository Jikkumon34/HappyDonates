from rest_framework import serializers
from .models import UserPostModel, UserDonationModel, UserProfileModel
from AdminApp.models import Poster, DistrictsModel, MainCategoryModel, SubCategoryModel,DonationCategoryModel
from django.contrib.auth.models import User

class UserPostSerializer(serializers.ModelSerializer):
    sub_category_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = UserPostModel
        fields = '__all__'

    def get_sub_category_name(self, obj):
        return obj.sub_category.sub_category_name if obj.sub_category else None

    def get_district_name(self, obj):
        return obj.location.district_name if obj.location else None

    def get_user_name(self, obj):
        return obj.user.username if obj.user else None

    # def validate_sub_category(self, value):
    #     try:
    #         return int(value)
    #     except ValueError:
    #         raise serializers.ValidationError("Sub category must be an integer.")
    #
    # def validate_location(self, value):
    #     try:
    #         return int(value)
    #     except ValueError:
    #         raise serializers.ValidationError("Location must be an integer.")


class UserDonationSerializer(serializers.ModelSerializer):
    donation_category_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = UserDonationModel
        fields = '__all__'

    def get_donation_category_name(self, obj):
        return obj.category.donation_category_name if obj.category else None

    def get_district_name(self, obj):
        return obj.location.district_name if obj.location else None

    def get_user_name(self, obj):
        return obj.user.username if obj.user else None


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfileModel.
    """

    class Meta:
        model = UserProfileModel
        fields = ['user_profile_id', 'profile_image', 'phone', 'user']


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistrictsModel
        fields = ['district_id', 'district_name', 'state_id']


class PosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poster
        fields = ['id', 'title', 'status', 'image', 'date_posted']


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategoryModel
        fields = ['sub_category_id', 'sub_category_name', 'main_category_id']


class MainCategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True, source='subcategories')

    class Meta:
        model = MainCategoryModel
        fields = ['main_category_id', 'main_category_name', 'subcategories']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']



class DonationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationCategoryModel
        fields = ['donation_category_id', 'donation_category_name']
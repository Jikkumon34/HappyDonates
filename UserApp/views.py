from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import UserPostModel, UserDonationModel, UserProfileModel
from django.contrib.auth.models import User
from AdminApp.models import DistrictsModel, Poster, MainCategoryModel, SubCategoryModel,DonationCategoryModel
from .serializers import UserPostSerializer, UserDonationSerializer, UserProfileSerializer, PosterSerializer, \
    DistrictSerializer, SubCategorySerializer, MainCategorySerializer, UserSerializer,DonationCategorySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['POST'])
def register_user(request):
    """
    Register a new user.
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)


@api_view(['POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def saveOrUpdate_user_post(request, post_id=None):
    """
    Create a new user post.

    This endpoint allows users to create a new post by providing the necessary details in a POST request.

    Parameters:
        request (Request): The HTTP request object containing the post data.

    Returns: Response: A JSON response containing the serialized post data if successful, along with a status code
    201 (Created). If the request data is invalid, it returns error messages along with a status code 400 (Bad Request).
    :param request:
    :param post_id:
    """
    user = request.user
    if post_id is not None:
        try:
            post = UserPostModel.objects.select_related('user', 'sub_category', 'location').get(pk=post_id,user=user)
            if request.method == 'PUT':
                serializer = UserPostSerializer(instance=post, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            elif request.method == 'DELETE':
                post.delete()
                return Response({"message": "Post deleted successfully"}, status=status.HTTP_200_OK)
        except UserPostModel.DoesNotExist:
            return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserPostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def fetch_post(request, post_id=None):
    """
    Fetch user posts.

    This endpoint retrieves user posts based on optional query parameters. It accepts both GET and POST requests.
    If a post_id is provided, it fetches a single post by its ID.

    Parameters:
        request (Request): The HTTP request object.
        post_id (int, optional): ID of the post to fetch.

    Returns:
        Response: A JSON response containing the serialized post data if successful, along with a status code 200 (OK).
                  If the requested post is not found, it returns an error message with a status code 404 (Not Found).
                  For any other errors, it returns an error message along with a status code 500 (Internal Server Error).
    """

    try:
        if post_id is not None:
            post = UserPostModel.objects.select_related('user', 'sub_category', 'location').get(pk=post_id)
            serialized_post = UserPostSerializer(post, many=False).data
            return Response(serialized_post, status=status.HTTP_200_OK)

        if request.method == 'GET':
            query_params = request.query_params
            filters = Q()
            for key, value in query_params.items():
                if value:
                    if key == 'query':
                        filters &= (Q(title__icontains=value) | Q(description__icontains=value))
                    elif key == 'start_date':
                        filters &= Q(create_at__gte=value)
                    elif key == 'location':
                        filters &= Q(location__district_name__icontains=value)
                    elif key == 'subcategory':
                        filters &= Q(sub_category__sub_category_name__icontains=value)
                    elif key == 'main_category':
                        filters &= Q(sub_category__main_category_id__main_category_name=value)

                    elif key == 'end_date':
                        filters &= Q(create_at__lte=value)
                    else:
                        filters &= Q(**{key: value})

            posts = UserPostModel.objects.select_related('user', 'sub_category', 'location').filter(
                filters) if filters else UserPostModel.objects.select_related('user', 'sub_category', 'location').all()
            posts = posts.filter(status="Active")

            serialized_posts = UserPostSerializer(posts, many=True).data

            return Response(serialized_posts, status=status.HTTP_200_OK)

    except UserPostModel.DoesNotExist:
        return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def saveOrUpdate_user_donation(request, donation_id=None):
    """
    Create a new user donation.

    This endpoint allows users to create a new donation request by providing the necessary details in a POST request.

    Parameters:
        request (Request): The HTTP request object containing the donation data.

    Returns:
        Response: A JSON response containing the serialized donation data if successful, along with a status code 201 (Created).
                  If the request data is invalid, it returns error messages along with a status code 400 (Bad Request).
                  :param request:
                  :param donation_id:

    """
    user = request.user
    if donation_id is not None:
        try:
            donation = UserDonationModel.objects.select_related('user', 'category', 'location').get(pk=donation_id)
            if request.method == 'PUT':
                serializer = UserDonationSerializer(donation, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            elif request.method == 'DELETE':
                donation.delete()
                return Response({"message": "Donation deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except UserDonationModel.DoesNotExist:
            return Response({"message": "Donation not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserDonationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def fetch_donation(request, donation_id=None):
    """
    Fetch user donations.

    This endpoint retrieves user donations based on optional query parameters. It accepts both GET and POST requests.
    If a donation_id is provided, it fetches a single donation by its ID.

    Parameters:
        request (Request): The HTTP request object.
        donation_id (int, optional): ID of the donation to fetch.

    Returns:
        Response: A JSON response containing the serialized donation data if successful, along with a status code 200 (OK).
                  If the requested donation is not found, it returns an error message with a status code 404 (Not Found).
                  For any other errors, it returns an error message along with a status code 500 (Internal Server Error).
    """
    try:
        if donation_id is not None:
            donation = UserDonationModel.objects.select_related('user', 'category', 'location').get(pk=donation_id)
            serialized_donation = UserDonationSerializer(donation, many=False).data
            return Response(serialized_donation, status=status.HTTP_200_OK)

        if request.method == 'GET':
            query_params = request.query_params
            filters = Q()
            for key, value in query_params.items():
                if value:
                    if key == 'query':
                        filters &= (Q(title__icontains=value) | Q(description__icontains=value))
                    elif key == 'start_date':
                        filters &= Q(create_at__gte=value)
                    elif key == 'location':
                        filters &= Q(location__district_name__icontains=value)
                    elif key == 'category':
                        filters &= Q(category__donation_category_name__icontains=value)
                    elif key == 'end_date':
                        filters &= Q(create_at__lte=value)
                    else:
                        filters &= Q(**{key: value})

            donations = UserDonationModel.objects.select_related('user', 'category', 'location').filter(
                filters) if filters else UserDonationModel.objects.select_related('user', 'category', 'location').all()
            donations = donations.filter(status="Active")

            serialized_donations = UserDonationSerializer(donations, many=True).data

            return Response(serialized_donations, status=status.HTTP_200_OK)

    except UserDonationModel.DoesNotExist:
        return Response({"message": "Donation not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request, user_id):
    """
    Retrieve or update user profile data.

    Parameters:
        request (Request): The HTTP request object.
        user_id (int): The ID of the user whose profile is being retrieved or updated.

    Returns:
        Response: A JSON response containing the serialized user profile data if successful,
                  along with a status code 200 (OK) for GET request.
                  If the user profile is updated successfully, it returns a status code 200 (OK).
                  If the request data is invalid, it returns error messages along with a status code 400 (Bad Request).
                  If the requested user profile does not exist, it returns an error message with a status code 404 (Not Found).
                  For any other errors, it returns an error message along with a status code 500 (Internal Server Error).
    """
    try:
        profile = UserProfileModel.objects.get(user_id=user_id)
    except UserProfileModel.DoesNotExist:
        return Response({"message": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def all_districts(request):
    """
    Retrieve all districts.
    """
    if request.method == 'GET':
        districts = DistrictsModel.objects.all()
        serializer = DistrictSerializer(districts, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def all_posters(request):
    """
    Retrieve all posters.
    """

    if request.method == 'GET':
        posters = Poster.objects.filter(status=True)
        serializer = PosterSerializer(posters, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def subcategories_by_main_category(request, main_category_id):
    """
    Retrieve all subcategories by main category id.
    """
    try:
        main_category = MainCategoryModel.objects.get(pk=main_category_id)
    except MainCategoryModel.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    subcategories = SubCategoryModel.objects.filter(main_category_id=main_category)
    serializer = SubCategorySerializer(subcategories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    """
    Endpoint to get authenticated user's information.
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_posts_and_donations(request):
    """
    Endpoint to get authenticated user's posts and donations.
    """
    user = request.user
    posts = UserPostModel.objects.filter(user=user)
    donations = UserDonationModel.objects.filter(user=user)
    post_serializer = UserPostSerializer(posts, many=True)
    donation_serializer = UserDonationSerializer(donations, many=True)
    return Response({
        'posts': post_serializer.data,
        'donations': donation_serializer.data
    })

@api_view(['GET'])
def donation_category_list(request):
    donation_categories = DonationCategoryModel.objects.all()
    serializer = DonationCategorySerializer(donation_categories, many=True)
    return Response(serializer.data)


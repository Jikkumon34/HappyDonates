from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Count, Q, Subquery, OuterRef, Sum, F
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import date
from .models import *
from UserApp.models import *
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json


@login_required(login_url='/admin_login')
def home(request):
    """
    Renders the admin home page with statistics and graph data from the models.

    :param request: HTTP request object.
    :return: Rendered admin home page with statistics.
    """
    user_data = []
    for month in range(1, 13):
        user_count = User.objects.filter(date_joined__month=month).count()
        user_data.append(user_count)

    post_data = []
    for month in range(1, 13):
        post_count = UserPostModel.objects.filter(create_at__month=month).count()
        post_data.append(post_count)

    donation_data = []
    for month in range(1, 13):
        donation_count = UserDonationModel.objects.filter(create_at__month=month).count()
        donation_data.append(donation_count)

    data = {
        'user_count': User.objects.filter(is_active=True).count(),
        'post_count': UserPostModel.objects.filter(status="Active").count(),
        'donation_count': UserDonationModel.objects.all().count(),
        'donation_request': UserDonationModel.objects.filter(status="Pending",
                                                             category__donation_category_id=1).order_by('end_date'),
        'user_data': user_data,
        'post_data': post_data,
        'donation_data': donation_data,
    }
    return render(request, 'admin_home_page.html', data)

def admin_login(request):
    """
    Handles the admin login process.

    :param request: HTTP request object.
    :return: Redirects to home page if login is successful, else renders admin login page.
    """
    if request.method == 'POST':
        admin_username = request.POST.get('admin_username')
        admin_password = request.POST.get('admin_password')

        user = authenticate(username=admin_username, password=admin_password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('/admin_home')
            else:
                return render(request, 'admin_login.html', {'error': 'You do not have admin privileges.'})
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid username or password.'})
    return render(request, 'admin_login.html')


@login_required(login_url='/admin_login')
def admin_user(request):
    """
    Renders the admin user page with user statistics and search functionality.

    :param request: HTTP request object.
    :return: Rendered admin user page with user statistics and search results.
    """
    data_user = {
        'user_count': User.objects.filter(is_active=True).count(),
        'user_month_count': User.objects.filter(is_active=True,
                                                date_joined__month=timezone.now().month,
                                                date_joined__year=timezone.now().year).count(),
        'user_year_count': User.objects.filter(is_active=True,
                                               date_joined__year=timezone.now().year).count(),
        'user_today_count': User.objects.filter(is_active=True,
                                                date_joined__date=date.today()).count(),
        'user_data': User.objects.annotate(post_count=Count('posts')).order_by('-date_joined')
    }

    if request.method == "POST":
        search = request.POST.get("userSearch", "")
        start_date = request.POST.get("startDate")
        end_date = request.POST.get("endDate")
        status = request.POST.get("userStatus")
        countFetch = request.POST.get("userCount", 0)

        results = User.objects.annotate(post_count=Count('posts')).filter(
            Q(username__icontains=search)
        )

        if start_date and end_date:
            results = results.filter(date_joined__range=[start_date, end_date])

        if status:
            if status == 'active':
                results = results.filter(is_active=True)
            elif status == 'inactive':
                results = results.filter(is_active=False)

        if countFetch.isdigit() and int(countFetch) > 0:
            results = results.order_by('-date_joined')[:int(countFetch)]

        data_user['user_data'] = results

    return render(request, "admin_user_page.html", data_user)


@login_required(login_url='/admin_login')
def admin_post(request):
    """
    Renders the admin post page with post statistics, search, and filtering functionality.

    :param request: HTTP request object.
    :return: Rendered admin post page with post statistics, search results, and filtering options.
    """
    data_post = {
        'post_count': UserPostModel.objects.filter(status="Active").count(),
        'post_month_count': UserPostModel.objects.filter(status="Active",
                                                         create_at__month=timezone.now().month,
                                                         create_at__year=timezone.now().year).count(),
        'post_year_count': UserPostModel.objects.filter(status="Active",
                                                        create_at__year=timezone.now().year).count(),
        'post_today_count': 0,
        'post_data': UserPostModel.objects.all().order_by('-create_at'),
        'subCategory': SubCategoryModel.objects.all().order_by('sub_category_name'),
        'Districts': DistrictsModel.objects.all().order_by('district_name'),
    }

    if request.method == "POST":
        search = request.POST.get("postSearch")
        start_date = request.POST.get("startDate")
        end_date = request.POST.get("endDate")
        postCategory = request.POST.get("postCategory")
        postLocation = request.POST.get("postLocation")
        status = request.POST.get("PostStatus")
        countFetch = request.POST.get("PostCount", 0)

        results = UserPostModel.objects.filter(
            Q(title__icontains=search) | Q(description__icontains=search) | Q(
                address__icontains=search) |
            Q(address__icontains=search) |
            Q(user__username__icontains=search)
        )

        if start_date and end_date:
            results = results.filter(create_at__range=[
                start_date, end_date]).order_by('-create_at')
        if postLocation != "Location":
            results = results.filter(
                location=DistrictsModel.objects.get(district_id=int(postLocation))).order_by('-create_at')
        if postCategory != "Category":
            results = results.filter(
                sub_category=SubCategoryModel.objects.get(sub_category_id=int(postCategory))).order_by(
                '-create_at')
        if status:
            if status == 'active':
                results = results.filter(status="Active")
            elif status == 'inactive':
                results = results.filter(status='Inactive')

        if countFetch.isdigit() and int(countFetch) > 0:
            results = results.order_by('-create_at')[:int(countFetch)]
        data_post['post_data'] = results
    return render(request, "admin_post_page.html", data_post)


@login_required(login_url='/admin_login')
def admin_category(request):
    """
    Renders the admin category page with post statistics categorized by subcategories.

    :param request: HTTP request object.
    :return: Rendered admin category page with post statistics categorized by subcategories.
    """
    data_post = {
        'post_count': UserPostModel.objects.filter(status="Active").count(),
        'post_month_count': UserPostModel.objects.filter(status="Active",
                                                         create_at__month=timezone.now().month,
                                                         create_at__year=timezone.now().year).count(),
        'post_year_count': UserPostModel.objects.filter(status="Active",
                                                        create_at__year=timezone.now().year).count(),
        'post_today_count': UserPostModel.objects.filter(status="Active",
                                                         create_at__date=date.today()).count(),
        'post_data': UserPostModel.objects.all().order_by('-create_at'),
        'subCategoryFood': SubCategoryModel.objects.annotate(count=Count('posts')).filter(main_category_id=1),
        'subCategoryNonFood': SubCategoryModel.objects.annotate(count=Count('posts')).filter(main_category_id=2)
    }

    return render(request, "admin_category_page.html", data_post)


@login_required(login_url='/admin_login')
def admin_add_category(request):
    """
    Adds a new subcategory to the main category.

    :param request: HTTP request object.
    :return: Redirects to admin subcategory page after adding the new subcategory.
    """
    if request.method == "POST":
        sub_category_name = request.POST.get("subCategoryName", '').strip()
        main_category_id = int(request.POST.get("mainCategory"))

        mainCategory = MainCategoryModel.objects.get(main_category_id=main_category_id)
        data = SubCategoryModel.objects.filter(sub_category_name__iexact=sub_category_name,
                                               main_category_id=mainCategory)
        if data:
            return render(request, 'admin_add_subcategory.html', {'status': "invalid"})
        else:
            subCategory = SubCategoryModel(main_category_id=mainCategory, sub_category_name=sub_category_name)
            subCategory.save()
            return redirect('/admin_subcategory')

    return render(request, 'admin_add_subcategory.html')


@login_required(login_url='/admin_login')
def admin_remove_subcategory(request, id):
    """
    Removes a subcategory.

    :param request: HTTP request object.
    :param id: ID of the subcategory to be removed.
    :return: Redirects to admin subcategory page after removing the subcategory.
    """
    sub_categoryFood = SubCategoryModel.objects.filter(sub_category_id=id, main_category_id=1)
    data = SubCategoryModel.objects.get(sub_category_id=id)

    if sub_categoryFood:
        UserPostModel.objects.filter(sub_category=data).update(
            sub_category_id=4
        )
    else:
        UserPostModel.objects.filter(sub_category=data).update(
            sub_category_id=5
        )

    data.delete()
    return redirect('/admin_subcategory')


@login_required(login_url='/admin_login')
def admin_donation_request(request):
    """
    Renders the admin donation request page with donation statistics and filtered donations.

    :param request: HTTP request object.
    :return: Rendered admin donation request page with donation statistics and filtered donations.
    """
    data_donation_request = {
        'donation_count': UserDonationModel.objects.count(),
        'active_donation_count': UserDonationModel.objects.filter(status="Active").count(),
        'donation_month_count': UserDonationModel.objects.filter(
            create_at__month=timezone.now().month,
            create_at__year=timezone.now().year
        ).count(),
        'donation_request_year_count': UserDonationModel.objects.filter(
            create_at__year=timezone.now().year
        ).count(),
        'location': DistrictsModel.objects.all(),
        'category': DonationCategoryModel.objects.all(),
        'donations': UserDonationModel.objects.all().order_by('create_at')
    }

    if request.method == "POST":
        search = request.POST.get("donationSearch", "")
        start_date = request.POST.get("startDate")
        end_date = request.POST.get("endDate")
        status = request.POST.get("donationStatus")
        countFetch = request.POST.get("donationCount", 0)
        location = request.POST.get("donationLocation")
        category = request.POST.get("donationCategory")

        results = UserDonationModel.objects.all().order_by('create_at')

        if search:
            results = results.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(address__icontains=search) |
                Q(hospital_name__icontains=search) |
                Q(donation_user_name__icontains=search) |
                Q(contact_number__icontains=search) |
                Q(comments__icontains=search) |
                Q(user__username__icontains=search)
            )

        if start_date and end_date:
            results = results.filter(create_at__range=[start_date, end_date])

        if status:
            results = results.filter(status=status)

        if location:
            results = results.filter(location__district_id=int(location))

        if category:
            results = results.filter(category__donation_category_id=int(category))

        if countFetch.isdigit() and int(countFetch) > 0:
            results = results[:int(countFetch)]

        data_donation_request['donations'] = results

    return render(request, 'admin_donation_request.html', {'donation_request': data_donation_request})


@login_required(login_url='/admin_login')
def state_district_view(request):
    """
    Renders the state and district view with annotated data for posts and donations.

    :param request: HTTP request object.
    :return: Rendered state and district view with annotated data.
    """
    districts = DistrictsModel.objects.annotate(
        total_donations=Count('donations')
    )

    states = StateModel.objects.annotate(
        total_posts=Count('districts__posts'),
        total_donations=Count('districts__donations')
    )

    context = {'states': states, 'districts': districts}
    return render(request, 'admin_state_district.html', context)


@login_required(login_url='/admin_login')
def user_profile(request, user_name):
    """
    Renders the user profile page with user posts and donations.

    :param request: HTTP request object.
    :param user_name: Username of the user whose profile is to be viewed.
    :return: Rendered user profile page with user posts and donations.
    """
    user = get_object_or_404(User, username=user_name)
    user_posts = UserPostModel.objects.filter(user=user)
    user_donations = UserDonationModel.objects.filter(user=user)

    context = {
        'user': user,
        'user_posts': user_posts,
        'user_donations': user_donations,
    }

    return render(request, 'admin_user_profile.html', context)


@login_required(login_url='/admin_login')
def update_user_status(request, action, user_id):
    """
    Updates the status of a user (activate, deactivate, delete).

    :param request: HTTP request object.
    :param action: Action to be performed (inactive, activate, delete).
    :param user_id: ID of the user whose status is to be updated.
    :return: JsonResponse indicating success or failure of the action.
    """
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            if action == 'inactive':
                user.is_active = False
                user.save()
                return JsonResponse({'success': True})
            elif action == 'activate':
                user.is_active = True
                user.save()
                return JsonResponse({'success': True})
            elif action == 'delete':
                user.delete()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required(login_url='/admin_login')
def post_detail_view(request, post_id):
    """
    Renders the post detail view with post and user data.

    :param request: HTTP request object.
    :param post_id: ID of the post to be viewed.
    :return: Rendered post detail view with post and user data.
    """
    post = get_object_or_404(UserPostModel, pk=post_id)
    user = post.user
    user_posts = UserPostModel.objects.filter(user=user)

    context = {
        'user': user,
        'post': post,
        'user_posts': user_posts,
    }

    return render(request, 'admin_post_details.html', context)

@login_required(login_url='/admin_login')
def donation_detail_view(request, donation_id):
    """
    Renders the donation detail view with donation and user data.

    :param request: HTTP request object.
    :param donation_id: ID of the donation to be viewed.
    :return: Rendered donation detail view with donation and user data.
    """
    donation = get_object_or_404(UserDonationModel, donation_id=donation_id)
    user = donation.user
    other_donations = UserDonationModel.objects.filter(user=user).exclude(donation_id=donation_id)

    context = {
        'donation': donation,
        'user': user,
        'other_donations': other_donations,
    }
    return render(request, 'admin_donation_details.html', context)


def update_donation_status(request, action, donation_id):
    """
    Updates the status of a donation (approve, reject, inactive, active, delete).

    :param request: HTTP request object.
    :param action: Action to be performed on the donation.
    :param donation_id: ID of the donation whose status is to be updated.
    :return: JsonResponse indicating success or failure of the action.
    """
    if request.method == 'POST':
        donation = get_object_or_404(UserDonationModel, donation_id=donation_id)

        if action == 'approve':
            donation.status = 'Active'
        elif action == 'reject':
            donation.status = 'Reject'
        elif action == 'inactive':
            donation.status = 'Inactive'
        elif action == 'active':
            donation.status = 'Active'
        elif action == 'delete':
            donation.delete()
            return JsonResponse({'success': True, 'deleted': True})

        donation.save()
        return JsonResponse({'success': True, 'status': donation.status})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def update_post_status(request, action, post_id):
    """
    Updates the status of a post (approve, reject, inactive, active, delete).

    :param request: HTTP request object.
    :param action: Action to be performed on the post.
    :param post_id: ID of the post whose status is to be updated.
    :return: JsonResponse indicating success or failure of the action.
    """
    if request.method == 'POST':
        post = get_object_or_404(UserPostModel, post_id=post_id)

        if action == 'approve':
            post.status = 'Active'
        elif action == 'reject':
            post.status = 'Reject'
        elif action == 'inactive':
            post.status = 'Inactive'
        elif action == 'active':
            post.status = 'Active'
        elif action == 'delete':
            post.delete()
            return JsonResponse({'success': True, 'deleted': True})

        post.save()
        return JsonResponse({'success': True, 'status': post.status})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def add_state(request):
    if request.method == 'POST':
        state_name = request.POST.get('state_name')
        if state_name:
            state = StateModel()
            state.state_name = state_name
            state.save()
            return JsonResponse({'success': True, 'state_id': state.state_id, 'state_name': state.state_name})
        return JsonResponse({'success': False, 'error': 'Invalid data'})


def add_district(request):
    if request.method == 'POST':
        district_name = request.POST.get('district_name')
        state_id = request.POST.get('state_id')
        if district_name and state_id:
            state = StateModel.objects.get(pk=state_id)
            district = DistrictsModel()
            district.district_name = district_name
            district.state_id = state
            district.save()
            return JsonResponse(
                {'success': True, 'district_id': district.district_id, 'district_name': district.district_name,
                 'state_name': state.state_name})
        return JsonResponse({'success': False, 'error': 'Invalid data'})


def delete_state(request, state_id):
    try:
        state = StateModel.objects.get(pk=state_id)
        state.delete()
        return JsonResponse({'success': True})
    except StateModel.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'State not found'})


def delete_district(request, district_id):
    try:
        district = DistrictsModel.objects.get(pk=district_id)
        district.delete()
        return JsonResponse({'success': True})
    except DistrictsModel.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'District not found'})

@login_required(login_url='/admin_login')
def poster_list(request):
    posters = Poster.objects.all()
    context = {
        'posters': posters,
        'poster_count': posters.count()
    }
    return render(request, 'admin_poster_list.html', context)


@csrf_exempt
def add_poster(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        if title and image:
            poster = Poster.objects.create(title=title, image=image)
            return JsonResponse({'success': True, 'poster_id': poster.id})
    return JsonResponse({'success': False})


@csrf_exempt
def change_status(request, poster_id):
    poster = get_object_or_404(Poster, id=poster_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        status = data.get('status')
        poster.status = status == 'True'
        poster.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@csrf_exempt
def delete_poster(request, poster_id):
    poster = get_object_or_404(Poster, id=poster_id)
    if request.method == 'POST':
        poster.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def admin_logout(request):
    try:
        logout(request)
        return redirect('admin_login')
    except:
        return redirect('admin_login')

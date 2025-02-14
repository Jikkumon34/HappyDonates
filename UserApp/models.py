from django.contrib.auth.models import User
from django.db import models
from AdminApp.models import SubCategoryModel, DonationCategoryModel, DistrictsModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserPostModel(models.Model):
    """
    Model representing posts made by users.

    Attributes:
        post_id (AutoField): The primary key for the post.
        user (ForeignKey): The user who made the post.
        title (CharField): The title of the post.
        description (TextField): The description of the post.
        quantity (IntegerField): The quantity of items in the post.
        sub_category (ForeignKey): The subcategory of the post.
        pick_up_time (DateTimeField): The pick-up time for the post.
        end_on (DateTimeField): The end time for the post (nullable).
        location (ForeignKey): The location of the post.
        address (TextField): The address of the post.
        images (ImageField): The image(s) associated with the post.
        contact_number (CharField): The contact number for the post.
        comments (TextField): Any additional comments on the post (nullable).
        create_at (DateTimeField): The creation time of the post.
        status (CharField): The status of the post.

    Meta:
        db_table (str): The name of the database table for the model.
    """
    post_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', null=True)
    title = models.CharField(max_length=250, null=True)
    description = models.TextField(null=True)
    quantity = models.IntegerField(default=1)
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE, related_name='posts', null=True)
    pick_up_time = models.DateTimeField(null=True)
    end_on = models.DateTimeField(null=True, )
    location = models.ForeignKey(DistrictsModel, on_delete=models.CASCADE, related_name='posts', null=True)
    address = models.TextField(null=True)
    images = models.ImageField(upload_to='images/', null=True)
    contact_number = models.CharField(max_length=100, null=True)
    comments = models.TextField(max_length=300, null=True)

    create_at = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=100, default="Active")

    class Meta:
        db_table = 'user_post_table'


@receiver(post_save, sender=UserPostModel)
def update_status(sender, instance, **kwargs):
    if instance.end_on and instance.end_on < timezone.now() and instance.status == 'Active':
        instance.status = 'Inactive'
        instance.save()


class UserDonationModel(models.Model):
    """
    Model representing donation requests made by users.

    Attributes:
        donation_id (AutoField): The primary key for the donation request.
        user (ForeignKey): The user who made the donation request.
        title (CharField): The title of the donation request.
        description (TextField): The description of the donation request.
        category (ForeignKey): The category of the donation request.
        end_date (DateTimeField): The end date for the donation request.
        location (ForeignKey): The location of the donation request.
        address (CharField): The address of the donation request.
        images (ImageField): The image(s) associated with the donation request.
        contact_number (CharField): The contact number for the donation request.
        comments (TextField): Any additional comments on the donation request.
        create_at (DateTimeField): The creation time of the donation request.
        status (CharField): The status of the donation request.

    Meta:
        db_table (str): The name of the database table for the model.
    """
    donation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations', null=True)
    title = models.CharField(max_length=400, null=True)
    description = models.TextField(null=True)
    category = models.ForeignKey(DonationCategoryModel, on_delete=models.CASCADE, related_name='donations', null=True)
    end_date = models.DateTimeField(null=True)
    location = models.ForeignKey(DistrictsModel, on_delete=models.CASCADE, related_name='donations', null=True)
    address = models.CharField(max_length=500, null=True)
    donation_file = models.FileField(upload_to='files/', null=True, default=None)
    hospital_name = models.CharField(max_length=500, null=True, default=None)
    donation_user_name = models.CharField(max_length=500, null=True)
    hospital_patient_id = models.CharField(max_length=500, null=True)
    images = models.ImageField(upload_to='images/', null=True)
    contact_number = models.CharField(max_length=100, null=True)
    comments = models.TextField(max_length=500, null=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=100, default="Pending")

    class Meta:
        db_table = 'user_donation_table'


class UserProfileModel(models.Model):
    """
    Model representing images uploaded by users.

    Attributes:
        user_image_id (AutoField): The primary key for the user image.
        user_image (ImageField): The image uploaded by the user.
        user_phone (CharField): The phone number of the user.
        user (OneToOneField): The user who uploaded the image.

    Meta:
        db_table (str): The name of the database table for the model.
    """
    user_profile_id = models.AutoField(primary_key=True)
    profile_image = models.ImageField(null=True)
    phone = models.CharField(max_length=200, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='image')

    class Meta:
        db_table = "user_profile_table"

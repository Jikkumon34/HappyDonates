from django.db import models


class MainCategoryModel(models.Model):
    """
    Model representing main categories.

    Attributes:
        main_category_id (IntegerField): The primary key for the main category.
        main_category_name (CharField): The name of the main category.

    Meta:
        db_table (str): The name of the database table for the model.
    """
    main_category_id = models.IntegerField(primary_key=True)
    main_category_name = models.CharField(max_length=100)

    class Meta:
        db_table = "main_category_table"


class SubCategoryModel(models.Model):
    """
    Model representing subcategories.

    Attributes:
        sub_category_id (AutoField): The primary key for the subcategory.
        sub_category_name (CharField): The name of the subcategory.
        main_category_id (ForeignKey): The main category to which the subcategory belongs.

    Meta:
        db_table (str): The name of the database table for the model.
    """
    sub_category_id = models.AutoField(primary_key=True)
    sub_category_name = models.CharField(max_length=100)
    main_category_id = models.ForeignKey(
        MainCategoryModel, on_delete=models.CASCADE)

    class Meta:
        db_table = "sub_category_table"


class DonationCategoryModel(models.Model):
    """
    Model representing donation categories.

    Attributes:
        donation_category_id (IntegerField): The primary key for the donation category.
        donation_category_name (CharField): The name of the donation category.

    Meta:
        db_table (str): The name of the database table for the model.
    """
    donation_category_id = models.IntegerField(primary_key=True)
    donation_category_name = models.CharField(max_length=100)

    class Meta:
        db_table = "donation_category_table"


class StateModel(models.Model):
    """
    Model representing states.

    Attributes:
        state_id (IntegerField): The primary key for the state.
        state_name (CharField): The name of the state.

    Meta:
        db_table (str): The name of the database table for the model.
    """
    state_id = models.AutoField(primary_key=True)
    state_name = models.CharField(max_length=100)

    def __str__(self):
        return  self.state_name

    class Meta:
        db_table = "state_data_table"


class DistrictsModel(models.Model):
    """
    Model representing districts.

    Attributes:
        district_id (IntegerField): The primary key for the district.
        district_name (CharField): The name of the district.
        state_id (ForeignKey): The state to which the district belongs.

    Meta:
        db_table (str): The name of the database table for the model.
    """
    district_id = models.AutoField(primary_key=True)
    district_name = models.CharField(max_length=100)
    state_id = models.ForeignKey(StateModel, on_delete=models.CASCADE,related_name='districts')

    class Meta:
        db_table = "districts_data_table"
    def __str__(self):
        return self.district_name


class Poster(models.Model):
    title = models.CharField(max_length=200)
    status = models.BooleanField(default=True)
    image = models.ImageField(upload_to='posters/')
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

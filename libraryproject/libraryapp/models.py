from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Account(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    address=models.CharField(max_length=255)
    phone=models.CharField(max_length=10)
    image=models.ImageField(blank=True,upload_to='image/')
    status=models.IntegerField(default=0)

class Books(models.Model):
    bookname=models.CharField(max_length=100)
    description=models.CharField(max_length=100)
    authorname=models.CharField(max_length=100)
    publisher_id=models.CharField(max_length=20)
    stock=models.IntegerField(default=0)
    price=models.IntegerField(null=True)
    bookimage=models.ImageField(blank=True,upload_to='image/')

class Rental(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    book=models.ForeignKey(Books,on_delete=models.CASCADE,null=True)
    rentaldate=models.DateField()
    duedate=models.DateField()
    returned=models.IntegerField(default=0)
    lost=models.IntegerField(default=0)
    fine=models.IntegerField(default=0)
    quantity=models.IntegerField(default=1)
    uviewed=models.IntegerField(default=0)
    aviewed=models.IntegerField(default=0)
    

class Purchase(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    book=models.ForeignKey(Books,on_delete=models.CASCADE,null=True)
    quantity=models.IntegerField(default=1)
    purchasedate=models.DateField()
    purchasestatus=models.IntegerField(default=0)

# class Notifications(models.Model):
#     user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
#     book=models.ForeignKey(Books,on_delete=models.CASCADE,null=True)
#     rent=models.ForeignKey(Rental,on_delete=models.CASCADE,null=True)
#     status=models.IntegerField(default=0)
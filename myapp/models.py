from django.contrib.auth.models import User
from django.db import models



class UserProfile(models.Model):
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    photo = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    dob= models.DateField()
    place = models.CharField(max_length=100)
    bio = models.CharField(max_length=100)
    account_type = models.CharField(max_length=100)
    status=models.CharField(max_length=100)

class Complaints(models.Model):
    USER=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    complaints = models.CharField(max_length=100)
    date = models.DateField()
    reply = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

class Review(models.Model):
    USER=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    date = models.DateField()
    review = models.CharField(max_length=200)
    rating = models.CharField(max_length=200)

class Post(models.Model):
    USER=models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    photo= models.CharField(max_length=300)
    date = models.DateField()
    caption = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

class Request(models.Model):
    FROM= models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name="frmr")
    TO=models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name="tor")
    time = models.TimeField()
    status = models.CharField(max_length=100)
    date = models.DateField()


class Like(models.Model):
    USER=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    POST=models.ForeignKey(Post,on_delete=models.CASCADE)
    time = models.TimeField()
    date = models.DateField()




class Comments(models.Model):
    time = models.TimeField()
    date = models.DateField()
    comments = models.CharField(max_length=500)
    USER=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    POST=models.ForeignKey(Post,on_delete=models.CASCADE)
    type = models.CharField(max_length=200)

class Messagechat(models.Model):
    FROM = models.ForeignKey(User, on_delete=models.CASCADE,related_name="fromc")
    TO = models.ForeignKey(User, on_delete=models.CASCADE, related_name="toc")
    time = models.TimeField()
    date = models.DateField()
    message = models.CharField(max_length=200)

#
# class Notifications(models.Model):
#     POST= models.ForeignKey(Post, on_delete=models.CASCADE)
#     time = models.TimeField()
#     date = models.DateField()
#     status = models.CharField(max_length=100)
#     notification = models.CharField(max_length=100)

class Notifications(models.Model):
    POST= models.ForeignKey(Post, on_delete=models.CASCADE)
    USER= models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    time = models.TimeField()
    date = models.DateField()
    status = models.CharField(max_length=100)
    bottom = models.CharField(max_length=100)
    left = models.CharField(max_length=100)
    right = models.CharField(max_length=100)
    top = models.CharField(max_length=100)
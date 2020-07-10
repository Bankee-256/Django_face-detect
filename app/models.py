from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('male', "男"),
        ('female', "女"),
    )
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default="male")


class Result(models.Model):
    pic_id = models.IntegerField(primary_key=True)
    pic_path = models.CharField(max_length=1024, default='#')
    date = models.DateTimeField(auto_now=True)
    authorization = models.BooleanField(default=False)

    # 与UserProfile关联的外键
    userProfile = models.ForeignKey('UserProfile', on_delete=models.CASCADE)

    # output:
    age = models.IntegerField(default=18)
    gender = models.CharField(max_length=1024, default='male')
    value = models.DecimalField(decimal_places=3, max_digits=5, default=0)
    expression = models.CharField(max_length=1024, default='smile')
    face_shape = models.CharField(max_length=1024, default='heart')
    glasses = models.CharField(max_length=1024, default='no glass')

    # thumbs up times
    thumbsUpTime = models.IntegerField(default=0)

    class Meta:
        permissions = (
            ('thumbs_up', 'can give user thumbs up'),
            ('make_comments', 'can make comments'),
            ('high_quality_voice', 'can get result with high quality voice'),
            ('get_top_face', 'can get top 8 of all faces'),
        )


class Like(models.Model):
    like_id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    pic_id = models.IntegerField()
    is_like = models.BooleanField(default=False)

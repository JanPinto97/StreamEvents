from django.contrib.auth.models import AbstractUser
from djongo import models

class CustomUser(AbstractUser):
    # Camps extra
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    # Necessita Pillow instal·lat

    def __str__(self):
        return self.username


class Follow(models.Model):
    # follower (A) segueix following (B)
    follower = models.ForeignKey(
        'CustomUser',
        related_name='following_set',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        'CustomUser',
        related_name='followers_set',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # Evita duplicats A->B

    def __str__(self):
        return f'{self.follower} -> {self.following}'
    
class Event(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    #password1 = models.CharField(max_length=128)
    #password2 = models.CharField(max_length=128)

    def __str__(self):
        return self.username
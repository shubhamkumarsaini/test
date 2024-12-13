from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required')
        email = self.normalize_email(email)


        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, max_length=150)
    full_name = models.CharField(max_length=30, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class TVShow(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name='tv_shows')
    air_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title


class Episode(models.Model):
    show = models.ForeignKey(TVShow, on_delete=models.CASCADE, related_name='episodes')
    season = models.IntegerField()
    episode_number = models.IntegerField()
    air_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.show.title} - Season {self.season}, Episode {self.episode_number}"


class EpisodeImage(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='episode_images/')
    order = models.IntegerField(help_text="Order of appearance for guessing (1 to 6)")

    def __str__(self):
        return f"Image for {self.episode} (Order {self.order})"


class DailyGame(models.Model):
    date = models.DateField(unique=True)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='daily_games')

    def __str__(self):
        return f"Game for {self.date}"


class UserGameHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_history')
    game = models.ForeignKey(DailyGame, on_delete=models.CASCADE, related_name='user_histories')
    guesses = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    correct_guess = models.BooleanField(default=False)

    def __str__(self):
        return f"History of {self.user.username} for {self.game}"


class UserStatistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='statistics')
    total_games_played = models.IntegerField(default=0)
    total_correct_guesses = models.IntegerField(default=0)
    win_streak = models.IntegerField(default=0)
    highest_win_streak = models.IntegerField(default=0)

    def __str__(self):
        return f"Stats for {self.user.username}"



from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **kwargs):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError("Users must have a username.")
        if email is None:
            raise TypeError("Users must have an email.")

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError("Superusers must have a password.")
        if email is None:
            raise TypeError("Superusers must have an email.")
        if username is None:
            raise TypeError("Superusers must have an username.")

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255)
    email = models.EmailField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(
        ('staff status'),
        default=False,
        help_text=('Designates whether the user can log into this admin site.'),
        null=True,
        blank=True
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return f"{self.email}"


class ApiKeyModel(models.Model):
    key = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)


class AutoBalancerModel(models.Model):
    loadbalancer_name = models.TextField()
    loadbalancer_tag = models.CharField(max_length=1000)
    minimun_droplets = models.IntegerField()
    maximum_droplets = models.IntegerField()
    droplet_tag = models.CharField(max_length=1000)
    threshold_CPU = models.FloatField()
    threshold_Load1 = models.FloatField(blank=True, null=True)
    threshold_load5 = models.FloatField(blank=True, null=True)
    threshold_load15 = models.FloatField(blank=True, null=True)
    is_runing = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)




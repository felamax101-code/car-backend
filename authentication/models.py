from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with a role field.

    - DRIVER accounts are created by drivers themselves via the public
      registration endpoint (role is forced server-side).
    - ADMIN and GATE_OPERATOR accounts are NOT self-registrable. They
      are created upfront by a superuser: through Django admin, or by
      running `python manage.py seed_staff` once at project setup.
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        GATE_OPERATOR = "GATE_OPERATOR", "Gate Operator"
        DRIVER = "DRIVER", "Driver"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.DRIVER)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"{self.username} ({self.role})"
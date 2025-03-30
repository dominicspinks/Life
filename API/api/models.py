from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class ModuleType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class UserModule(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    module = models.ForeignKey(ModuleType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order = models.IntegerField()
    is_enabled = models.BooleanField(default=False)
    is_read_only = models.BooleanField(default=False)
    is_checkable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class FieldType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class FieldTypeRule(models.Model):
    field_type = models.ForeignKey(FieldType, on_delete=models.CASCADE)
    rule = models.CharField(max_length=255)

    def __str__(self):
        return self.rule

class ListField(models.Model):
    user_module = models.ForeignKey(UserModule, on_delete=models.CASCADE)
    field_type = models.ForeignKey(FieldType, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    is_mandatory = models.BooleanField(default=False)

    def __str__(self):
        return self.field_name

class ListFieldRule(models.Model):
    list_field = models.ForeignKey(ListField, on_delete=models.CASCADE)
    field_type_rule = models.ForeignKey(FieldTypeRule, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.list_field.field_name} - {self.field_type_rule.rule}"

class ListItem(models.Model):
    user_module = models.ForeignKey(UserModule, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_module.name} - {self.modified_at}"

class ListItemField(models.Model):
    list_item = models.ForeignKey(ListItem, on_delete=models.CASCADE)
    list_field = models.ForeignKey(ListField, on_delete=models.CASCADE)
    field_value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.list_field.field_name} - {self.field_value}"

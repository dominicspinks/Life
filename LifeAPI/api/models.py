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
    order = models.IntegerField()

    def __str__(self):
        return self.field_name

class ListFieldRule(models.Model):
    list_field = models.ForeignKey(ListField, on_delete=models.CASCADE)
    field_type_rule = models.ForeignKey(FieldTypeRule, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.list_field.field_name} - {self.field_type_rule.rule}"

class ListFieldOption(models.Model):
    list_field = models.ForeignKey(ListField, on_delete=models.CASCADE)
    option_name = models.CharField(max_length=255)

    def __str__(self):
        return self.option_name

class ListItem(models.Model):
    user_module = models.ForeignKey(UserModule, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    modified_at = models.DateTimeField(auto_now=True)
    fields = models.JSONField(default=list)

    def __str__(self):
        return f"{self.user_module.name} - {self.modified_at}"


class BudgetCategory(models.Model):
    user_module = models.ForeignKey(UserModule, on_delete=models.CASCADE)
    name = models.TextField()
    weekly_target = models.IntegerField(default=0)
    excluded_from_budget = models.BooleanField(default=False)
    order = models.IntegerField()
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_module', 'name')
        ordering = ['order']

    def __str__(self):
        return self.name

class BudgetPurchase(models.Model):
    user_module = models.ForeignKey(UserModule, on_delete=models.CASCADE)
    purchase_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True,blank=True)
    category = models.ForeignKey(BudgetCategory, on_delete=models.SET_NULL, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchase_date', '-modified_at']

    def __str__(self):
        return f"{self.purchase_date} - {self.description or ''}"

class Period(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class BudgetCashFlow(models.Model):
    user_module = models.ForeignKey(UserModule, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True,blank=True)
    is_income = models.BooleanField(default=False)
    period = models.ForeignKey(Period, on_delete=models.PROTECT, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description or ''} - ${self.amount}"


class BudgetTermType(models.Model):
    word_length = models.IntegerField(unique=True)
    weight = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['word_length'], name='idx_termtype_wordlength'),
        ]

    def __str__(self):
        return f"{self.word_length}-gram"

class BudgetCategoryTermFrequency(models.Model):
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE)
    term = models.CharField(max_length=255)
    term_type = models.ForeignKey(BudgetTermType, on_delete=models.PROTECT)
    frequency = models.IntegerField(default=0)

    class Meta:
        unique_together = ('category', 'term', 'term_type')
        indexes = [
            models.Index(fields=['term_type', 'term'], name='idx_termtype_term'),
            models.Index(fields=['category', 'term_type'], name='idx_category_termtype'),
        ]

    def __str__(self):
        return self.term
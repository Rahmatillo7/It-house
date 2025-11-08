from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ============================
class Lead(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)  # Facebook, Instagram, va h.k.

    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'operator'},
        related_name="leads"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = [
        ('new', 'Bog\'lanish kerak'),
        ('info_given', 'Malumot berildi'),
        ('meeting_scheduled', 'Uchrashuv belgilandi'),
        ('meeting_done', 'Uchrashuv o\'tkazildi'),
        ('not_reached', 'Bog\'lana olmadik'),
        ('sold', 'Sotildi'),
        ('not_sold', 'Sotilmadi'),
        ('no_show', 'Uchrashuvga kelmadi'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


# ============================
# Task model
# ============================
class Task(models.Model):
    operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'operator'},
        related_name="tasks"
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    description = models.TextField()
    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    penalty = models.FloatField(default=0.0)  # Jarima ballari

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"Task for {self.operator.username} -> {self.lead.full_name}"


# ============================
# SMS model
# ============================
class SMS(models.Model):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="sms_messages"
    )
    operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'operator'},
        related_name="sent_sms"
    )
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"SMS to {self.lead.phone} by {self.operator.username}"


# ============================
# Student model
# ============================
class Student(models.Model):
    lead = models.OneToOneField(
        Lead,
        on_delete=models.CASCADE,
        related_name="student"
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Student)"


# ============================
# Contract model
# ============================
class Contract(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="contracts"
    )
    course_name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'operator'},
        related_name="contracts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contract {self.student.name} - {self.course_name}"

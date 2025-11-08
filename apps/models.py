from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Branch(Base):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Operator(Base):
    class StatusType(models.TextChoices):
        INTERN = 'Intern', 'Intern'
        WORKER = 'Worker', 'Worker'

    class StatusGender(models.TextChoices):
        MALE = 'Male', 'Male'
        FEMALE = 'Female', 'Female'

    full_name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusType.choices)
    phone_number = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='operator_photos/', blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    penalty = models.IntegerField(default=0)
    gender = models.CharField(max_length=10, choices=StatusGender.choices)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='operators')

    def __str__(self):
        return self.full_name

    def add_penalty(self, points=1):
        self.penalty += points
        self.save(update_fields=['penalty'])

class Lead(Base):
    class Status(models.TextChoices):
        NEED_CONTACT = "need_contact", "Need Contact"
        INFO_PROVIDED = "info_provided", "Information Provided"
        MEETING_SCHEDULED = "meeting_scheduled", "Meeting Scheduled"
        MEETING_CANCELLED = "meeting_cancelled", "Meeting Cancelled"
        COULD_NOT_CONTACT = "could_not_contact", "Could Not Contact"
        SOLD = "sold", "Sold"
        NOT_SOLD = "not_sold", "Not Sold"
        DID_NOT_SHOW_UP = "did_not_show_up", "Did Not Show Up"

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=50, choices=Status.choices, default='new')
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")
    source = models.CharField(max_length=100, blank=True, null=True)
    demo_date = models.DateTimeField(blank=True, null=True)
    last_contact_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Lead"
        verbose_name_plural = "Leadlar"

    def __str__(self):
        return f"{self.full_name} ({self.get_status_display()})"

class Task(Base):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name="tasks")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    penalty_points = models.IntegerField(default=0)

    def mark_completed(self):
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save(update_fields=['is_completed', 'completed_at'])

    def __str__(self):
        return f"{self.title} ({'Bajarilgan' if self.is_completed else 'Bajarilmagan'})"

class Penalty(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name="penalties")
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=255)
    points = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Jarima"
        verbose_name_plural = "Jarimalar"

    def apply_penalty(self):
        self.operator.add_penalty(self.points)

class SMS(Base):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="sms_messages"
    )
    operator = models.ForeignKey(
        "apps.Operator",
        on_delete=models.CASCADE,
        related_name="sent_sms"
    )
    provider_sms_sid = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"SMS to {self.lead.phone} by {self.operator.user.username if self.operator.user else 'unknown'}"


class Contract(Base):
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name="contracts")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="contracts")
    course_name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.course_name
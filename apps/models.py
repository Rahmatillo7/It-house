from django.db import models
from django.db.models import TextChoices, CharField, ForeignKey, CASCADE, Model

class Base(Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Lead(Base):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)

    operator = models.ForeignKey(
        "apps.Operator",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads"
    )

    class StatusChoices(TextChoices):
        NEW = 'New' , 'new'
        INFO_GIVEN = 'Info_given' , 'info_given'
        MEETING_SCHEDULED = 'Meeting_scheduled' , 'meeting_scheduled'
        MEETING_DONE = 'Meeting_done' , 'meeting_done'
        NOT_REACHED = 'Not_reached' , 'not_reached'
        SOLD = 'Sold' , 'sold'
        NOT_SOLD = 'Not_sold', 'not_sold'
        NO_SHOW = 'No_show', 'no_show'


    status = models.CharField(max_length=20, choices=StatusChoices, default='new')

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

class Operator(Base):
    class StatusType(TextChoices):
        INTERN = 'Intern', 'intern',
        WORKER = 'Worker', 'worker'

    class StatusGender(TextChoices):
        MALE = 'Male', 'male',
        FEMALE = 'Female', 'female'

    full_name = models.CharField(max_length=100)
    status = CharField(choices=StatusType)
    phone_number = models.CharField(max_length=20)
    penalty = models.IntegerField(blank=True, null=True)
    gender = CharField(choices=StatusGender)
    branch_id = ForeignKey("apps.Branch", CASCADE, related_name='operators')
    task_id = ForeignKey("apps.Task", CASCADE, related_name='operators', blank=True, null=True)

    def __str__(self):
        return self.full_name

class Task(Base):
    operator = models.ForeignKey(
        "apps.Operator",
        on_delete=models.CASCADE,
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



    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"Task for {self.operator.full_name} -> {self.lead.full_name}"


class Branch(Base):
    name = CharField(max_length=255)
    location = CharField(max_length=255)

    def __str__(self):
        return self.name




class Call(Base):
    DIRECTION_CHOICES = (
        ('outbound', 'Outbound'),  # Sizdan talaba tomon
        ('inbound', 'Inbound'),    # Talabadan sizga
    )


    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default='outbound')
    provider_call_sid = models.CharField(max_length=255, blank=True, null=True)  # Twilio yoki boshqa xizmat ID’si
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    recording_url = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.lead}"

    @property
    def duration_display(self):
        """Soniya emas, minut/sekund ko‘rinishida chiqarish uchun"""
        if not self.duration_seconds:
            return "–"
        minutes, seconds = divmod(self.duration_seconds, 60)
        return f"{minutes} min {seconds} sec"


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

    class Meta:
        ordering = ['-sent_at']

    def str(self):
        return f"SMS to {self.lead.phone} by {self.operator.username}"

class Penalty(Base):
    operator = models.ForeignKey('apps.Operator', on_delete=models.CASCADE, related_name="penalties")
    lead = models.ForeignKey('apps.Lead', on_delete=models.CASCADE, related_name="penalties")
    task = models.ForeignKey('apps.Task', on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=255)
    points = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.operator} -> {self.lead}"










#
# class Contract(Base):
#     student = models.ForeignKey(
#         Student,
#         on_delete=models.CASCADE,
#         related_name="contracts"
#     )
#     course_name = models.CharField(max_length=255)
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()
#     amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
#     operator = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         limit_choices_to={'role': 'operator'},
#         related_name="contracts"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def str(self):
#         return f"Contract {self.student.name} - {self.course_name}"

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Existing Expense Model
class Expense(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=266)

    def __str__(self):
        return self.category

    class Meta:
        ordering = ['-date']


# Existing Category Model
class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


# Existing ExpenseLimit Model
class ExpenseLimit(models.Model):
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    daily_expense_limit = models.IntegerField()


from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta

# New Bill Model
class Bill(models.Model):
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)  # Link the bill to the user
    name = models.CharField(max_length=255)  # Name of the bill (e.g., 'Electricity', 'Subscription')
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount of the bill
    due_date = models.DateField()  # Due date for the bill payment
    frequency = models.CharField(
        max_length=50, choices=[('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Monthly'
    )  # Recurrence frequency (Monthly or Yearly)
    description = models.TextField(blank=True, null=True)  # Optional description about the bill
    next_due_date = models.DateField(null=True, blank=True)  # Calculated next due date for recurring bills
    created_at = models.DateTimeField(auto_now_add=True)  # When the bill was created

    def __str__(self):
        return f'{self.name} - {self.amount}'

    def save(self, *args, **kwargs):
        # Automatically calculate the next_due_date based on frequency
        if not self.next_due_date:  # If next_due_date is not set, calculate it
            self.update_due_date()
        super().save(*args, **kwargs)

    # Custom method to calculate the next due date based on the frequency (Monthly or Yearly)
    def update_due_date(self):
        if self.frequency == 'Monthly':
            # For monthly bills, the next due date is one month after the current due date
            if self.due_date.month == 12:
                self.next_due_date = self.due_date.replace(year=self.due_date.year + 1, month=1)
            else:
                self.next_due_date = self.due_date.replace(month=self.due_date.month + 1)
        elif self.frequency == 'Yearly':
            # For yearly bills, the next due date is one year after the current due date
            self.next_due_date = self.due_date.replace(year=self.due_date.year + 1)

    class Meta:
        ordering = ['due_date']



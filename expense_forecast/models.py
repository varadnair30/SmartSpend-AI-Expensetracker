from django.db import models
from django.contrib.auth.models import User

# models.py
class UserBudget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255, blank=True, null=True)
    budget_amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=50, choices=[('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Monthly')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.category:
            return f'{self.category} - {self.budget_amount}'
        return f'Overall Budget - {self.budget_amount}'

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'category')  # Ensures one budget per category per user
from django.urls import path
from . import views

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="expenses"),
    path('add-expense', views.add_expense, name="add-expenses"),
    path('edit-expense/<int:id>', views.expense_edit, name="expense-edit"),
    path('expense-delete/<int:id>', views.delete_expense, name="expense-delete"),
    path('search-expenses', csrf_exempt(views.search_expenses),
         name="search_expenses"),
    path('expense_category_summary', views.expense_category_summary,
         name="expense_category_summary"),
    path('stats', views.stats_view,
         name="stats"),
    path('stats/data', views.expense_summary_data, name='expense_summary_data'),
    path('add-bill/', views.add_bill, name='add-bill'),
    path('set-daily-expense-limit/',views.set_expense_limit,name="set-daily-expense-limit")

]

# Serve static files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
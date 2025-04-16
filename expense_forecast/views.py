from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import UserBudget
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from expenses.models import Expense
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserBudget
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserBudget
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Add the view for setting the budget
from django.shortcuts import render, redirect
from .models import UserBudget
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# expense_forecast/views.py

@login_required(login_url='/authentication/login')
def forecast(request):
    # Fetch latest 30 expenses
    expenses = Expense.objects.filter(owner=request.user).order_by('-date')[:30]

    if len(expenses) < 10:
        messages.error(request, "Not enough expenses to make a forecast. Please add more expenses.")
        return render(request, 'expense_forecast/index.html')

    # Fetch user budget data (for comparison)
    user_budget = UserBudget.objects.filter(user=request.user, category='').first()
    category_budgets = UserBudget.objects.filter(user=request.user).exclude(category='')
    category_budgets_dict = {budget.category: budget.budget_amount for budget in category_budgets}

    # Build DataFrame
    data = pd.DataFrame({
        'Date': [expense.date for expense in expenses],
        'Expenses': [expense.amount for expense in expenses],
        'Category': [expense.category for expense in expenses]
    })

    # Clean & prepare data
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    data['Expenses'] = pd.to_numeric(data['Expenses'], errors='coerce')
    data.dropna(subset=['Date', 'Expenses'], inplace=True)
    data.sort_values('Date', inplace=True)
    data.set_index('Date', inplace=True)

    # Safety check again
    if data.empty or len(data['Expenses'].unique()) == 1:
        messages.error(request, "Not enough valid data for forecasting.")
        return render(request, 'expense_forecast/index.html')

    # ARIMA forecasting
    try:
        model = ARIMA(data['Expenses'], order=(5, 1, 0))
        model_fit = model.fit()

        forecast_steps = 30
        next_day = now().date() + pd.DateOffset(days=1)
        forecast_index = pd.date_range(start=next_day, periods=forecast_steps, freq='D')
        forecast = model_fit.forecast(steps=forecast_steps)
    except Exception as e:
        return HttpResponse(f"Forecasting failed: {str(e)}")

    # Forecast DataFrame
    forecast_data = pd.DataFrame({
        'Date': forecast_index,
        'Forecasted_Expenses': forecast
    })
    forecast_data_list = forecast_data.reset_index().to_dict(orient='records')
    total_forecasted_expenses = np.sum(forecast)

    # Category totals (safe)
    try:
        if 'Category' in data.columns and not data.empty and data['Category'].notna().any():
            cleaned_data = data.dropna(subset=['Category'])
            if not cleaned_data.empty:
                category_forecasts = cleaned_data.groupby(by='Category', axis=0)['Expenses'].sum().to_dict()
            else:
                category_forecasts = {}
        else:
            category_forecasts = {}
    except Exception as e:
        print("⚠️ Category groupby failed:", str(e))
        category_forecasts = {}

    # Calculate monthly average spending and generate AI budget suggestion
    avg_monthly_expense = total_forecasted_expenses  # This is for 30 days, so it's a monthly forecast
    
    # AI budget suggestion calculation (with 10% buffer for unexpected expenses)
    ai_suggestion = round(avg_monthly_expense * 1.10, 2)  # 10% buffer
    
    # Generate category-specific budget suggestions
    category_suggestions = {}
    for category, forecasted_amount in category_forecasts.items():
        # Add 10% buffer to category forecast
        category_suggestions[category] = round(forecasted_amount * 1.10, 2)

    # Compare forecasted expenses with user budgets and generate suggestions
    budget_comparison = {}
    for category, forecasted_expense in category_forecasts.items():
        if category in category_budgets_dict:
            budget_amount = category_budgets_dict[category]
            if forecasted_expense > budget_amount:
                budget_comparison[category] = {
                    'forecasted': forecasted_expense,
                    'budget': budget_amount,
                    'status': 'Over Budget',
                    'suggestion': category_suggestions.get(category, 0)
                }
            else:
                budget_comparison[category] = {
                    'forecasted': forecasted_expense,
                    'budget': budget_amount,
                    'status': 'Under Budget',
                    'suggestion': category_suggestions.get(category, 0)
                }
        else:
            budget_comparison[category] = {
                'forecasted': forecasted_expense,
                'budget': 'No Budget Set',
                'status': 'No Budget Set',
                'suggestion': category_suggestions.get(category, 0)
            }

    # Plot the forecast
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(data.index, data['Expenses'], label='Previous Expenses')
        plt.plot(forecast_index, forecast, label='Forecasted Expenses', color='red')
        plt.xlabel('Date')
        plt.ylabel('Expenses')
        plt.title('Expense Forecast for Next 30 Days')
        plt.legend()
        plt.tight_layout()

        plot_file = 'static/img/forecast_plot.png'
        plt.savefig(plot_file)
        plt.close()
    except Exception as e:
        print(f"⚠️ Plotting error: {e}")
        plot_file = ''

    # Render page
    context = {
        'forecast_data': forecast_data_list,
        'total_forecasted_expenses': total_forecasted_expenses,
        'category_forecasts': category_forecasts,
        'plot_file': plot_file,
        'budget_comparison': budget_comparison,
        'user_budget': user_budget,
        'ai_suggestion': ai_suggestion,
        'category_suggestions': category_suggestions
    }

    return render(request, 'expense_forecast/index.html', context)

@login_required(login_url='/authentication/login')
def set_budget(request):
    if request.method == 'POST':
        try:
            # Use empty string for overall budget instead of None
            category = request.POST.get('category', '')
            # Leave category as an empty string for overall budget
            
            budget_amount = request.POST.get('budget_amount')
            if not budget_amount:
                messages.error(request, "Please enter a budget amount.")
                return redirect('forecast')
                
            frequency = request.POST.get('frequency', 'Monthly')
            
            # Create or update the budget record
            user_budget, created = UserBudget.objects.update_or_create(
                user=request.user,
                category=category,  # Empty string for overall budget
                defaults={'budget_amount': budget_amount, 'frequency': frequency}
            )

            if created:
                msg = f"{'Category' if category else 'Overall'} budget set successfully!"
            else:
                msg = f"{'Category' if category else 'Overall'} budget updated successfully!"
                
            messages.success(request, msg)
            return redirect('forecast')
            
        except Exception as e:
            messages.error(request, f"Error setting budget: {str(e)}")
            return redirect('forecast')
    else:
        # Get existing budgets to display
        overall_budget = UserBudget.objects.filter(user=request.user, category='').first()
        category_budgets = UserBudget.objects.filter(user=request.user).exclude(category='')
        
        context = {
            'overall_budget': overall_budget,
            'category_budgets': category_budgets
        }
        return render(request, 'expense_forecast/set_budget.html', context)

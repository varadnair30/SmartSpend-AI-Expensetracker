from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from django.http import HttpResponse

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from expenses.models import Expense


@login_required(login_url='/authentication/login')
def forecast(request):
    # Fetch latest 30 expenses
    expenses = Expense.objects.filter(owner=request.user).order_by('-date')[:30]

    if len(expenses) < 10:
        messages.error(request, "Not enough expenses to make a forecast. Please add more expenses.")
        return render(request, 'expense_forecast/index.html')

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
        'plot_file': plot_file
    }

    return render(request, 'expense_forecast/index.html', context)

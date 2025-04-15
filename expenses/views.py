from django.shortcuts import render, redirect,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from django.contrib.sessions.models import Session
from datetime import date
from datetime import datetime
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
import datetime
from .models import ExpenseLimit
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .models import Expense
from django.http import JsonResponse
import datetime
from .models import Expense,Bill
from django.db.models import Sum
data = pd.read_csv('dataset.csv')

# Preprocessing
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
    return ' '.join(tokens)

data['clean_description'] = data['description'].apply(preprocess_text)

# Feature extraction
tfidf_vectorizer = TfidfVectorizer()
X = tfidf_vectorizer.fit_transform(data['clean_description'])

# Train a RandomForestClassifier
model = RandomForestClassifier()
model.fit(X, data['category'])
@login_required(login_url='/authentication/login')
def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def edit_bill(request, id):
    bill = Bill.objects.get(id=id)
    if request.method == 'POST':
        bill_name = request.POST['bill_name']
        bill_amount = request.POST['bill_amount']
        due_date = request.POST['due_date']
        frequency = request.POST['frequency']
        description = request.POST.get('description', '')  # Optional field

        try:
            # Convert the due_date string into a datetime object
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()

            # Calculate the next due date based on frequency
            if frequency == 'Monthly':
                next_due_date = due_date_obj.replace(month=due_date_obj.month + 1)  # Add one month
            elif frequency == 'Yearly':
                next_due_date = due_date_obj.replace(year=due_date_obj.year + 1)  # Add one year

            # Update the bill object
            bill.name = bill_name
            bill.amount = bill_amount
            bill.due_date = due_date_obj
            bill.frequency = frequency
            bill.description = description
            bill.next_due_date = next_due_date  # Store the calculated next_due_date
            bill.save()

            messages.success(request, 'Bill updated successfully')
            return redirect('expenses')  # Or wherever you want to redirect
        except Exception as e:
            messages.error(request, 'Error updating bill: ' + str(e))
            return redirect('bill-edit', id=id)  # Redirect to the same page if error

    context = {
        'bill': bill,
    }
    return render(request, 'expenses/edit_bill.html', context)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    bills = Bill.objects.filter(owner=request.user)  # Fetch the bills for the logged-in user

    sort_order = request.GET.get('sort')

    # Sorting logic for expenses
    if sort_order == 'amount_asc':
        expenses = expenses.order_by('amount')
        bills = bills.order_by('amount')
    elif sort_order == 'amount_desc':
        expenses = expenses.order_by('-amount')
        bills = bills.order_by('-amount')
    elif sort_order == 'date_asc':
        expenses = expenses.order_by('date')
        bills = bills.order_by('due_date')
    elif sort_order == 'date_desc':
        expenses = expenses.order_by('-date')
        bills = bills.order_by('-due_date')

    # Pagination for expenses
    paginator_expenses = Paginator(expenses, 5)
    paginator_bills = Paginator(bills, 5)

    page_number_expenses = request.GET.get('page')
    page_number_bills = request.GET.get('page_bills')

    page_obj_expenses = paginator_expenses.get_page(page_number_expenses)
    page_obj_bills = paginator_bills.get_page(page_number_bills)

    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = None

    # Total number of pages for both expenses and bills
    total_expenses = page_obj_expenses.paginator.num_pages
    total_bills = page_obj_bills.paginator.num_pages

    # Prepare context for rendering the template
    context = {
        'categories': categories,
        'expenses': expenses,
        'bills': bills,  # Add bills to the context
        'page_obj_expenses': page_obj_expenses,
        'page_obj_bills': page_obj_bills,  # Add bill page object to context
        'currency': currency,
        'total_expenses': total_expenses,
        'total_bills': total_bills,  # Add total bill count to context
        'sort_order': sort_order,
    }

    return render(request, 'expenses/index.html', context)


daily_expense_amounts = {}

@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        date_str = request.POST.get('expense_date')
        
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        predicted_category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expense.html', context)
        
        initial_predicted_category = request.POST.get('initial_predicted_category')
        if predicted_category != initial_predicted_category:
            new_data = {
            'description': description,
            'category': predicted_category,
        }

        update_url = 'http://127.0.0.1:8000/api/update-dataset/'
        response = requests.post(update_url, json={'new_data': new_data})

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()  # Correct date conversion
            today = datetime.today().date()  # Correct method to get today's date

            if date > today:
                messages.error(request, 'Date cannot be in the future')
                return render(request, 'expenses/add_expense.html', context)
            
            user = request.user
            expense_limits = ExpenseLimit.objects.filter(owner=user)
            if expense_limits.exists():
                daily_expense_limit = expense_limits.first().daily_expense_limit
            else:
                daily_expense_limit = 5000  

            
            total_expenses_today = get_expense_of_day(user) + float(amount)
            if total_expenses_today > daily_expense_limit:
                subject = 'Daily Expense Limit Exceeded'
                message = f'Hello {user.username},\n\nYour expenses for today have exceeded your daily expense limit. Please review your expenses.'
                from_email = settings.EMAIL_HOST_USER
                to_email = [user.email]
                send_mail(subject, message, from_email, to_email, fail_silently=False)
                messages.warning(request, 'Your expenses for today exceed your daily expense limit')

            Expense.objects.create(owner=request.user, amount=amount, date=date,
                                   category=predicted_category, description=description)
            messages.success(request, 'Expense saved successfully')
            return redirect('expenses')
        except ValueError:
            messages.error(request, 'Invalid date format')
            return render(request, 'expenses/add_expense.html', context)


from datetime import datetime
from dateutil.relativedelta import relativedelta  # Import relativedelta

@login_required(login_url='/authentication/login')
def add_bill(request):
    if request.method == 'POST':
        bill_name = request.POST['bill_name']
        bill_amount = request.POST['bill_amount']
        due_date = request.POST['due_date']
        frequency = request.POST['frequency']
        description = request.POST.get('description', '')  # Optional field

        try:
            # Convert the due_date string into a datetime object
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()

            # Calculate the next due date based on frequency using relativedelta
            if frequency == 'Monthly':
                next_due_date = due_date_obj + relativedelta(months=1)  # Add one month
            elif frequency == 'Yearly':
                next_due_date = due_date_obj + relativedelta(years=1)  # Add one year
            else:
                next_due_date = due_date_obj  # Default to the same due date if frequency is not recognized

            # Create the bill object
            Bill.objects.create(
                owner=request.user,
                name=bill_name,
                amount=bill_amount,
                due_date=due_date_obj,
                frequency=frequency,
                description=description,
                next_due_date=next_due_date  # Store the calculated next_due_date
            )

            messages.success(request, 'Bill added successfully')
            return redirect('expenses')  # Or redirect as needed

        except Exception as e:
            messages.error(request, 'Error adding bill: ' + str(e))
            return redirect('add-bill')  # Redirect to the same page if error

    return render(request, 'expenses/add_expense.html')




@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        date_str = request.POST.get('expense_date')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        try:
            # Convert the date string to a datetime object and validate the date
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            today = datetime.date.today()

            if date > today:
                messages.error(request, 'Date cannot be in the future')
                return render(request, 'expenses/add_expense.html', context)

            expense.owner = request.user
            expense.amount = amount
            expense. date = date
            expense.category = category
            expense.description = description

            expense.save()
            messages.success(request, 'Expense saved successfully')

            return redirect('expenses')
        except ValueError:
            messages.error(request, 'Invalid date format')
            return render(request, 'expenses/edit_income.html', context)

        # expense.owner = request.user
        # expense.amount = amount
        # expense. date = date
        # expense.category = category
        # expense.description = description

        # expense.save()

        # messages.success(request, 'Expense updated  successfully')

        # return redirect('expenses')

@login_required(login_url='/authentication/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')

@login_required(login_url='/authentication/login')
def delete_bill(request, id):
    try:
        # Fetch the bill object based on the given id
        bill = Bill.objects.get(pk=id)
        bill.delete()  # Delete the bill from the database

        # Display success message
        messages.success(request, 'Bill removed successfully.')

    except Bill.DoesNotExist:
        # If the bill doesn't exist, show an error message
        messages.error(request, 'Bill not found.')

    # Redirect to the expenses page or wherever you want to show the updated list
    return redirect('expenses')

@login_required(login_url='/authentication/login')
def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    
    finalrep = {}

    def get_category(expense):
        return expense.category

    # List of all categories in the selected date range
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    # Populate the dictionary with category as key and total amount as value
    for y in category_list:
        finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep})  # Properly returning JSON response



@login_required(login_url='/authentication/login')
def expense_summary(request):
    user = request.user

    # Fetching categories and their corresponding total expenses for the logged-in user
    categories = Expense.objects.filter(owner=user).values('category').annotate(total_amount=Sum('amount'))

    # Calculate total expenses for quick summary
    total_expenses = categories.aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'categories': categories,  # This will be a list of dictionaries containing category and total_amount
        'total_expenses': total_expenses,  # Total of all expenses
    }

    return render(request, 'income/stats.html', context)



@login_required(login_url='/authentication/login')
def expense_summary_data(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)

    finalrep = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    for y in category_list:
        finalrep[y] = get_expense_category_amount(y)

    # Return the data as a JSON response
    return JsonResponse({'expense_category_data': finalrep})




@login_required(login_url='/authentication/login')
def stats_view(request):
    expense_data = expense_category_summary(request).content  # .content will give you the JSON data
    expense_data = json.loads(expense_data)  # Convert byte data to a dictionary
    return render(request, 'expenses/stats.html', {'summary_data': expense_data})





@login_required(login_url='/authentication/login')
def predict_category(description):
    predict_category_url = 'http://localhost:8000/api/predict-category/'  # Use the correct URL path
    data = {'description': description}
    response = requests.post(predict_category_url, data=data)

    if response.status_code == 200:
        # Get the predicted category from the response
        predicted_category = response.json().get('predicted_category')
        return predicted_category
    else:
        # Handle the case where the prediction request failed
        return None
    

def set_expense_limit(request):
    if request.method == "POST":
        daily_expense_limit = request.POST.get('daily_expense_limit')
        
        existing_limit = ExpenseLimit.objects.filter(owner=request.user).first()
        
        if existing_limit:
            existing_limit.daily_expense_limit = daily_expense_limit
            existing_limit.save()
        else:
            ExpenseLimit.objects.create(owner=request.user, daily_expense_limit=daily_expense_limit)
        
        messages.success(request, "Daily Expense Limit Updated Successfully!")
        return HttpResponseRedirect('/preferences/')
    else:
        return HttpResponseRedirect('/preferences/')
    
def get_expense_of_day(user):
    current_date=date.today()
    expenses=Expense.objects.filter(owner=user,date=current_date)
    total_expenses=sum(expense.amount for expense in expenses)
    return total_expenses
    
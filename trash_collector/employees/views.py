from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Q
import calendar



from .models import Employee
Customer = apps.get_model('customers.Customer')
# Create your views here.

# TODO: Create a function for each path created in employees/urls.py. Each will need a template as well.

@login_required
def index(request):
    # This line will get the Customer model from the other app, it can now be used to query the db for Customers
    logged_in_user = request.user
    try:
        logged_in_employee = Employee.objects.get(user=logged_in_user)

        today = date.today()
        weekday = calendar.day_name[today.weekday()]
        
        customers = Customer.objects.filter(zip_code=logged_in_employee.zip_code)
        pickup_regular = customers.filter(weekly_pickup=weekday)
        pickup_one_time = customers.filter(one_time_pickup=today)
        scheduled_pickup = pickup_one_time | pickup_regular
        scheduled_pickup = scheduled_pickup.exclude (Q(suspend_start__lte=today) & Q(suspend_end__gte=today))
        scheduled_pickup = scheduled_pickup.exclude(date_of_last_pickup=today)
        

        context = {
            'logged_in_employee': logged_in_employee,
            'today': today,
            'weekday' : weekday,
            'scheduled_pickup' : scheduled_pickup
        }
        return render(request, 'employees/index.html', context)

    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('employees:create'))   

@login_required
def create(request):
    logged_in_user = request.user
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        zip_from_form = request.POST.get('zip_code')
        new_employee = Employee(name=name_from_form, user=logged_in_user, zip_code=zip_from_form)
        new_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        return render(request, 'employees/create.html')

@login_required
def edit_profile(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        zip_from_form = request.POST.get('zip_code')
        logged_in_employee.name = name_from_form
        logged_in_employee.zip_code = zip_from_form
        logged_in_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        context = {
            'logged_in_employee': logged_in_employee
        }
        return render(request, 'employees/edit_profile.html', context)

@login_required
def trash_picked_up(request, customer_id):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)    
    confirmed_customer = Customer.objects.get(pk=customer_id)
    confirmed_customer.balance += 20
    confirmed_customer.date_of_last_pickup = date.today()
    confirmed_customer.save()
    return HttpResponseRedirect(reverse('employees:index'))

@login_required
def filter_by_day(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    today = date.today()
    weekday = calendar.day_name[today.weekday()]
    if request.method == "POST":
        day_filter = request.POST.get('Weekday')
        filter_customers = Customer.objects.filter(weekly_pickup=day_filter)
        
        context = {
            'logged_in_employee': logged_in_employee,
            'day_filter': day_filter,
            'filter_customers': filter_customers,
            'weekday': weekday,
            'today': today
        }
        return render(request, 'employees/filter_by_day.html', context)

    else:
        context = {
            'logged_in_employee' : logged_in_employee
        }
        return render(request, 'employees/filter_by_day.html', context)

@login_required
def customer_info(request, customer_id):
    try:
        customer = Customer.objects.get(pk=customer_id)
        context = {
            'customer' : customer
        }
        return render(request, 'employees/customer_info.html', context )

    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('employees:index'))

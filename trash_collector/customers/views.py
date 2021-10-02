from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from datetime import date
import googlemaps
import requests
from .models import Customer
from django.conf import settings

gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
google_api_key = settings.GOOGLE_API_KEY

@login_required
def index(request):
    # The following line will get the logged-in user (if there is one) within any view function
    logged_in_user = request.user
    try:
        # This line will return the customer record of the logged-in user if one exists
        logged_in_customer = Customer.objects.get(user=logged_in_user)

        today = date.today()
        
        context = {
            'logged_in_customer': logged_in_customer,
            'today': today
        }
        return render(request, 'customers/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('customers:create'))

@login_required
def create(request):
    logged_in_user = request.user
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        address_from_form = request.POST.get('address')        
        zip_from_form = request.POST.get('zip_code')
        weekly_from_form = request.POST.get('weekly_pickup')
        geo_address = customer_geo(address_from_form, zip_from_form)
        geo_lat = geo_address[1]
        geo_lng = geo_address[2]
        new_customer = Customer(
            name=name_from_form, 
            user=logged_in_user, 
            address=address_from_form, 
            lat=geo_lat, 
            lng=geo_lng, 
            zip_code=zip_from_form, 
            weekly_pickup=weekly_from_form)
        new_customer.save()
        return HttpResponseRedirect(reverse('customers:index'))
    else:
        return render(request, 'customers/create.html')

@login_required
def suspend_service(request):
    logged_in_user = request.user
    logged_in_customer = Customer.objects.get(user=logged_in_user)
    if request.method == "POST":
        start_from_form = request.POST.get('start')
        end_from_form = request.POST.get('end')
        logged_in_customer.suspend_start = start_from_form
        logged_in_customer.suspend_end = end_from_form
        logged_in_customer.save()
        return HttpResponseRedirect(reverse('customers:index'))
    else:
        context = {
            'logged_in_customer': logged_in_customer
        }
        return render(request, 'customers/suspend.html', context)

@login_required
def one_time_pickup(request):
    logged_in_user = request.user
    logged_in_customer = Customer.objects.get(user=logged_in_user)
    if request.method == "POST":
        date_from_form = request.POST.get('date')
        logged_in_customer.one_time_pickup = date_from_form
        logged_in_customer.save()
        return HttpResponseRedirect(reverse('customers:index'))
    else:
        context = {
            'logged_in_customer': logged_in_customer
        }
        return render(request, 'customers/one_time.html', context)

@login_required
def edit_profile(request):
    logged_in_user = request.user
    logged_in_customer = Customer.objects.get(user=logged_in_user)
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        address_from_form = request.POST.get('address')
        zip_from_form = request.POST.get('zip_code')
        logged_in_customer.name = name_from_form
        logged_in_customer.address = address_from_form
        logged_in_customer.zip_code = zip_from_form
        logged_in_customer.save()
        return HttpResponseRedirect(reverse('customers:index'))
    else:
        context = {
            'logged_in_customer': logged_in_customer
        }
        return render(request, 'customers/edit_profile.html', context)


def customer_geo(address, zip_code):        
        full_address = f'{address} {zip_code}'
        api_response = requests.get(
            f'https://maps.googleapis.com/maps/api/geocode/json?address={full_address}&key={google_api_key}')
        geocode_result = api_response.json()
        lat = geocode_result['results'][0]['geometry']['location']['lat']
        lng = geocode_result['results'][0]['geometry']['location']['lng']
        return geocode_result, lat, lng

def submit_payment(request):
    logged_in_user = request.user
    logged_in_customer = Customer.objects.get(user=logged_in_user)
    if request.method == "POST":
        logged_in_customer.balance = 0
        logged_in_customer.save()
        return HttpResponseRedirect('https://buy.stripe.com/test_00geWW9F8b9b5VucMM')

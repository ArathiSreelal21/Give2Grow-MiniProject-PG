from django.shortcuts import render, redirect, get_object_or_404
from .models import Donation, Orphanage, EducationalInstitution, UserRegistration
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login as auth_login


# Index view
def index(request):
    return render(request, 'index.html')
def logout(request):
    return render(request,'index.html')
def about(request):
    return render(request,'about.html')
def causes(request):
    return render(request,'causes.html')

# User home view that shows donations only if the volunteer is approved
def userhome(request):
    # Filter donations based on their status (showing only picked or available items)
    picked_items = Donation.objects.filter(status='Picked')
    available_items = Donation.objects.filter(status='Available', approved_volunteer__is_approved=True)
    
    orphanages = Orphanage.objects.all()
    institutions = EducationalInstitution.objects.all()
    
    return render(request, 'user.html', {
        'picked_items': picked_items,
        'available_items': available_items,
        'orphanages': orphanages,
        'institutions': institutions
    })


# Volunteer home page
def vol(request):
    donations = Donation.objects.filter(status='Available')
    picked_donations = Donation.objects.filter(status='Picked')
    
    context = {
        'donations': donations,
        'picked_donations': picked_donations
    }
    return render(request, 'vol.html',context)

# Donation form view
def donate(request):
    return render(request, 'don.html')

# User registration view
def register(request):
    if request.method == 'POST':
        # Get form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Password confirmation check
        if password != confirm_password:
            return render(request, 'reg.html', {'error': 'Passwords do not match'})

        try:
            # Save the user registration data
            user = UserRegistration(
                full_name=full_name,
                email=email,
                user_type=user_type,
                password=make_password(password)  # Hash the password before saving
            )
            user.save()
            # Redirect to login page after successful registration
            return redirect('login')
        except IntegrityError:
            # Handle the case where the email already exists
            return render(request, 'reg.html', {'error': 'Email already exists'})

    return render(request, 'reg.html')

# Login view
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the user exists in the UserRegistration model
        try:
            user = UserRegistration.objects.get(email=email)

            # Check if the password matches (using hashed password)
            if check_password(password, user.password):
                # Optionally check if user.is_approved
                if user.is_approved:
                    # Log the user in (custom login handling)
                    request.session['user_id'] = user.id  # Set the user id in the session
                    request.session['user_email'] = user.email  # Store email or any other info if needed
                    return redirect('userhome')  # Redirect to a home or dashboard page
                else:
                    messages.error(request, 'Your account is not approved.')
            else:
                messages.error(request, 'Invalid password.')

        except UserRegistration.DoesNotExist:
            messages.error(request, 'Invalid email.')

    return render(request, 'login.html')
# View to approve volunteers (admin view)
def approve_volunteer(request, volunteer_id):
    volunteer = get_object_or_404(UserRegistration, id=volunteer_id)

    if request.method == 'POST':
        volunteer.is_approved = True
        volunteer.save()
        return redirect('volunteer_list')  # Redirect to the volunteer list after approval

    return render(request, 'approve_volunteer.html', {'volunteer': volunteer})

# View to list volunteers for approval (admin view)
def volunteer_list(request):
    volunteers = UserRegistration.objects.filter(user_type='Volunteer', is_approved=False)
    return render(request, 'volunteer_list.html', {'volunteers': volunteers})

# Function to assign a volunteer to a donation
def assign_volunteer_to_donation(request, donation_id, volunteer_id):
    donation = get_object_or_404(Donation, id=donation_id)
    volunteer = get_object_or_404(UserRegistration, id=volunteer_id)

    # Ensure the volunteer is approved
    if volunteer.user_type == 'Volunteer' and volunteer.is_approved:
        donation.approved_volunteer = volunteer
        donation.save()

    return redirect('donation_list')
def add_institution(request):
    if request.method == 'POST':
        # Extract data from the form
        name = request.POST.get('name')
        institution_type = request.POST.get('type')
        address = request.POST.get('address')
        email = request.POST.get('email')

        # Save data based on institution type
        if institution_type == 'Educational':
            EducationalInstitution.objects.create(
                name=name, 
                institution_type='Educational Institution',
                location=address, 
                amount_needed=0  # Default value, adjust as needed
            )
        elif institution_type == 'Orphanage':
            Orphanage.objects.create(
                name=name, 
                location=address, 
                contact=email, 
                amount_needed=0  # Default value, adjust as needed
            )

        # Redirect after successful submission
        return render(request,'vol.html')  # Adjust redirect as necessary
    else:
        return render(request, 'vol.html')  #

from django.shortcuts import render, redirect
from .models import Donation
from decimal import Decimal

def donate(request):
    if request.method == 'POST':
        # Get the form data
        amount = Decimal(request.POST.get('amount'))
        donation_type = request.POST.get('donation_type')
        payment_method = request.POST.get('payment_method')

        # Validate the amount
        if amount < 1:
            return render(request, 'donate.html', {"error_message": "Please enter a valid amount."})

        # Save the donation to the database
        donation = Donation.objects.create(
            donation_type=donation_type,
            amount=amount
        )

        # Simulate dummy payment success
        if payment_method == 'dummy':
            return render(request, 'donate.html', {"payment_success": True})

        # For other payment methods, you can add logic here
        return redirect('donation_success')

    return render(request, 'donate.html')
#pick-up
def pick_up_donation(request, donation_id):
    if request.method == 'POST':
        # Fetch the donation object
        donation = get_object_or_404(Donation, id=donation_id)
        
        # Update the status of the donation
        donation.status = 'Picked up'  # Change the status
        # Set the current time for pickup
        donation.save()  # Save the updated donation
        
        return JsonResponse({'status': 'success', 'message': 'Donation status updated to Picked up.'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
from django.shortcuts import render, redirect
from .models import PaymentHistory
from django.core.mail import send_mail
import random

def generate_otp():
    return str(random.randint(100000, 999999))

def process_payment(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        amount = request.POST['amount']
        card_number = request.POST['card_number']
        expiry_date = request.POST['expiry_date']
        cvv = request.POST['cvv']
        
        # For security reasons, do not store card number and CVV
        card_last_four = card_number[-4:]

        # Generate OTP and send via email
        otp = generate_otp()
        send_mail(
            'Your OTP for Payment',
            f'Your OTP is {otp}',
            'noreply@example.com',
            [email],
            fail_silently=False,
        )

        # Save payment as pending
        payment = PaymentHistory.objects.create(
            name=name,
            email=email,
            amount=amount,
            otp=otp,
            card_last_four=card_last_four,
            status='Pending'
        )

        # Redirect to OTP verification page
        return redirect('verify_otp', payment_id=payment.id)
    
    return render(request, 'payment_form.html')


def verify_otp(request, payment_id):
    payment = PaymentHistory.objects.get(id=payment_id)

    if request.method == 'POST':
        entered_otp = request.POST['otp']

        if payment.otp == entered_otp:
            payment.status = 'Completed'
            payment.save()
            return render(request, 'success.html')
        else:
            payment.status = 'Failed'
            payment.save()
            return render(request, 'otp_verification.html', {'error': 'Invalid OTP', 'email': payment.email})

    return render(request, 'otp_verification.html', {'email': payment.email})

def add_donation(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        cause = request.POST.get('cause')
        food_type = request.POST.get('food_type')
        food_quantity = request.POST.get('food_quantity')
        amount = request.POST.get('amount')

        # Create a new Donation object
        new_donation = Donation(
            name=name,
            email=email,
            cause=cause,
            food_type=food_type,
            food_quantity=food_quantity,
            amount=amount
        )
        new_donation.save()

        return redirect('userhome')  # Redirect to a success page or home page

    return render(request, 'your_template.html')  # Replace with your actual template


def error(request):
    return render(request, 'error.html')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Request
import json


def add_request(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_requested = data.get('item_requested')
        quantity = data.get('quantity')

        # Create a new request entry
        new_request = Request.objects.create(
            user=request.user,
            item_requested=item_requested,
            quantity=quantity
        )
        return JsonResponse({'status': 'success', 'message': 'Request added successfully.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})





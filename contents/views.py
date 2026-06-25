from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout as django_logout
from .models import Donor, AdminProfile, Donation,DonationCategory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def donation_type_list_public(request):
    types = DonationCategory.objects.all()
    return render(request, 'donation_types.html', {'types': types})

def about_page(request):
    return render(request, 'about.html')

from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Donor, ActivityLog, AdminProfile  # pastikan AdminProfile ada import
from django.contrib.auth.models import User

def login_register(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'register':
            # Donor registration
            name = request.POST.get('fullname')
            ic = request.POST.get('ic')
            contact = request.POST.get('contact')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm = request.POST.get('confirm_password')

            if password != confirm:
                messages.error(request, "Passwords do not match.")
                return redirect('login_register')

            if Donor.objects.filter(emailAddress=email).exists():
                messages.error(request, "Email already registered.")
                return redirect('login_register')

            user = User.objects.create_user(username=email, email=email, password=password)
            user.is_active = True
            user.save()

            donor = Donor.objects.create(
                user=user,
                donorIC=ic,
                donorName=name,
                contactNumber=contact,
                emailAddress=email,
            )

            request.session['donor_id'] = donor.donorID
            messages.success(request, "Registration successful!")
            return redirect('donor_dashboard')

        elif form_type == 'login':
            role = request.POST.get('role')
            identifier = request.POST.get('identifier')
            password = request.POST.get('password')

            if role == 'donor':
                try:
                    user = User.objects.get(username=identifier)
                    if user.check_password(password) and not user.is_staff:
                        donor = Donor.objects.get(user=user)
                        request.session['donor_id'] = donor.donorID
                        return redirect('donor_dashboard')
                except:
                    pass
                messages.error(request, "Invalid email or password.")
                return redirect('login_register')

            elif role in ['treasurer', 'chairman']:
                user = authenticate(request, username=identifier, password=password)
                if user is not None and user.is_staff:
                    try:
                        profile = AdminProfile.objects.get(user=user)
                    except AdminProfile.DoesNotExist:
                        messages.error(request, "Admin profile not found.")
                        return redirect('login_register')

                    if role == 'treasurer' and profile.role == 'Treasurer':
                        login(request, user)
                        messages.success(request, "Treasurer login successful.")
                        return redirect('treasurer_dashboard')
                    elif role == 'chairman' and profile.role == 'Chairman':
                        login(request, user)
                        messages.success(request, "Chairman login successful.")
                        return redirect('chairman_dashboard')
                    else:
                        messages.error(request, f"You selected '{role}', but your account is registered as '{profile.role}'.")
                        return redirect('login_register')
                else:
                    messages.error(request, "Invalid username or password.")
                    return redirect('login_register')

    return render(request, 'login.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        ic = request.POST.get('ic')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('forgot_password')

        try:
            donor = Donor.objects.get(emailAddress=email, donorIC=ic)
            user = donor.user
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Password successfully reset! You can now log in.")
            return redirect('login_register')
        except Donor.DoesNotExist:
            messages.error(request, "No donor found with matching email and IC.")
            return redirect('forgot_password')

    return render(request, 'forgot_password.html')


def is_treasurer(user):
    return user.is_authenticated and user.groups.filter(name='Treasurer').exists()

def is_chairman(user):
    return user.is_authenticated and user.groups.filter(name='Chairman').exists()


from collections import defaultdict
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import Donation  # Pastikan model yang betul di-import


@user_passes_test(is_treasurer)
def treasurer_dashboard(request):
    # Group total amount per month
    monthly_data = Donation.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    monthly_totals = {}
    for entry in monthly_data:
        month_name = entry['month'].strftime('%B')
        monthly_totals[month_name] = float(entry['total'])

    # Group by donation_type per month
    donations = Donation.objects.annotate(
        month=TruncMonth('date')
    ).values('month', 'donation_type__name').annotate(
        total=Sum('amount')
    )

    monthly_category_totals = defaultdict(dict)
    donation_categories = set()

    for item in donations:
        month = item['month'].strftime('%B')
        category = item['donation_type__name']
        donation_categories.add(category)
        monthly_category_totals[month][category] = float(item['total'])

    context = {
        'monthly_totals': monthly_totals,
        'monthly_category_totals': dict(monthly_category_totals),
        'donation_categories': sorted(donation_categories),
    }
    return render(request, 'treasurer_dashboard.html', context)


@user_passes_test(is_chairman)
def chairman_dashboard(request):
    return render(request, 'chairman_dashboard.html')

def edit_profile(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('login_register')

    donor = get_object_or_404(Donor, donorID=donor_id)

    if request.method == 'POST':
        donor.donorName = request.POST.get('fullname')
        donor.donorIC = request.POST.get('ic')
        donor.contactNumber = request.POST.get('contact')
        donor.emailAddress = request.POST.get('email')
        donor.save()
        messages.success(request, "Profile updated successfully!")

    return render(request, 'edit_profile.html', {'donor': donor})


def donor_dashboard(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, "Please log in first.")
        return redirect('login_register')

    try:
        donor = Donor.objects.get(donorID=donor_id)
    except Donor.DoesNotExist:
        messages.error(request, "Donor account not found.")
        return redirect('login_register')

    # Safer: Filter by donor.user to avoid mismatch
    donations = Donation.objects.filter(donor__user=donor.user, status__iexact='Approved')

    total_donation = sum(d.amount for d in donations)
    total_donation_count = donations.count()
    latest_donation = donations.order_by('-date').first()

    context = {
        'donor': donor,
        'total_donation': total_donation,
        'total_donation_count': total_donation_count,
        'latest_donation': latest_donation,
    }
    return render(request, 'donor_dashboard.html', context)



def donation_history(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, "You must be logged in to view your donation history.")
        return redirect('login_register')

    donor = get_object_or_404(Donor, donorID=donor_id)
    user_donations = Donation.objects.filter(donor=donor).order_by('-date')
    return render(request, 'donation_history.html', {'donations': user_donations})

def make_donation(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, "Please log in first.")
        return redirect('login_register')

    donor = get_object_or_404(Donor, donorID=donor_id)
    donation_categories = DonationCategory.objects.all()

    if request.method == 'POST':
        donation_type_id = request.POST.get('donation_type')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        card_number = request.POST.get('card_number', '').strip()
        proof = request.FILES.get('qr_receipt')

        # Get DonationCategory object
        try:
            donation_type = DonationCategory.objects.get(id=donation_type_id)
        except DonationCategory.DoesNotExist:
            messages.error(request, "Invalid donation type selected.")
            return redirect('make_donation')

        if payment_method == 'Credit/Debit Card' and (not card_number or len(card_number) < 13):
            messages.error(request, "Please enter a valid card number (min 13 digits).")
            return redirect('make_donation')

        qr_receipt_file = None
        if payment_method == 'QR Code' and proof:
            fs = FileSystemStorage()
            filename = fs.save(proof.name, proof)
            qr_receipt_file = filename

        donation = Donation.objects.create(
            donor=donor,
            donation_type=donation_type,
            amount=amount,
            payment_method=payment_method,
            card_number=card_number if payment_method == 'Credit/Debit Card' else None,
            qr_receipt=qr_receipt_file,
            status='Pending',
        )

        ActivityLog.objects.create(
    user=donor.user,
    role='Donor',
    action='Donation',
    description=f"Made donation RM {donation.amount} for '{donation.donation_type.name}'"
)

        return redirect('confirm_donation', donation_id=donation.id)

    return render(request, 'make_donation.html', {
        'donation_types': donation_categories,  # SEND REAL OBJECTS
        'payment_methods': Donation.PAYMENT_METHODS
    })

def confirm_donation(request, donation_id):
    print("=== confirm_donation ===")
    print("Donor ID after redirect:", request.session.get('donor_id'))
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, "Please log in first.")
        return redirect('login_register')

    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'confirm_donation.html', {'donation': donation})

def donation_receipt(request, donation_id):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, "Please log in first.")
        return redirect('login_register')

    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donation_receipt.html', {'donation': donation})


#ADMIN FUNCTIONS


@staff_member_required
def admin_dashboard(request):
    profile = AdminProfile.objects.get(user=request.user)
    full_name = request.user.first_name + " " + request.user.last_name
    all_donations = Donation.objects.all().order_by('-date')
    return render(request, 'admin_dashboard.html', {
        'profile': profile,
        'donations': all_donations,
        'full_name': full_name
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Donation

def manage_transactions(request):
    selected_status = request.GET.get('status')

    if selected_status:
        transactions = Donation.objects.filter(status=selected_status)
    else:
        transactions = Donation.objects.all()

    context = {
        'transactions': transactions,
        'selected_status': selected_status
    }
    return render(request, 'manage_transactions.html', context)


def update_transaction_status(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['Approved', 'Rejected']:
            donation.status = action
            donation.save()
            # Dalam update_transaction_status selepas .save()
            ActivityLog.objects.create(
    user=request.user,
    role='Treasurer',
    action='Approve' if action == 'Approved' else 'Reject',
    description=f"{action} donation RM {donation.amount} by {donation.donor.donorName}"
)

            messages.success(request, f'Donation has been {action.lower()} successfully.')
        else:
            messages.error(request, 'Invalid action.')

    return redirect('manage_transactions')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DonationCategory, AdminProfile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def is_treasurer(user):
    try:
        return AdminProfile.objects.get(user=user).role == 'Treasurer'
    except AdminProfile.DoesNotExist:
        return False
    


@login_required
def donation_type_list_admin(request):
    if not is_treasurer(request.user):
        messages.error(request, "Access denied.")
        return redirect('index')

    types = DonationCategory.objects.all()
    pending_requests = DonationCategoryRequest.objects.filter(status='pending')
    approved_requests = DonationCategoryRequest.objects.filter(status='approved')
    rejected_requests = DonationCategoryRequest.objects.filter(status='rejected')

    return render(request, 'manage_donations.html', {
        'types': types,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
    })


@login_required
def add_donation_type(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        # Get treasurer's AdminProfile
        profile = AdminProfile.objects.get(user=request.user)

        # Create request for chairman
        DonationCategoryRequest.objects.create(
            treasurer=profile,
            requested_by=request.user,
            action='create',
            name=name,
            description=description,
            status='pending',
            data_before='',
            data_after=f"Name: {name}, Description: {description}"
        )

        ActivityLog.objects.create(
    user=request.user,
    role='Treasurer',
    action='Request',
    description=f"Requested new donation type: '{name}'"
)

        messages.success(request, f"Your request to add '{name}' has been sent to the Chairman.")
        return redirect('donation_type_list_treasurer')

    return render(request, 'add_donation_type.html')
@login_required
def edit_donation_type(request, type_id):
    if not is_treasurer(request.user):
        messages.error(request, "Access denied.")
        return redirect('index')

    donation_type = get_object_or_404(DonationCategory, id=type_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if name:
            # Simpan data lama (sebelum update)
            data_before = f"Name: {donation_type.name}, Description: {donation_type.description}"
            data_after = f"Name: {name}, Description: {description}"

            try:
                treasurer_profile = AdminProfile.objects.get(user=request.user)
            except AdminProfile.DoesNotExist:
                messages.error(request, "Treasurer profile not found.")
                return redirect('donation_type_list_treasurer')

            DonationCategoryRequest.objects.create(
                treasurer=treasurer_profile,
                name=name,
                description=description,
                action='update',
                original_category=donation_type,
                requested_by=request.user,
                data_before=data_before,
                data_after=data_after
            )

            ActivityLog.objects.create(
                user=request.user,
                role='Treasurer',
                action='update',
                description=f"Requested update for donation type ID {donation_type.id} to '{name}'"
            )

            messages.success(request, "Edit request submitted for approval.")
            return redirect('donation_type_list_treasurer')

        else:
            messages.error(request, "Name cannot be empty.")

    return render(request, 'edit_donation_type.html', {'donation_type': donation_type})

@login_required
def delete_donation_type(request, type_id):
    if not is_treasurer(request.user):
        messages.error(request, "Access denied.")
        return redirect('index')

    donation_type = get_object_or_404(DonationCategory, id=type_id)
    donation_type.delete()

    ActivityLog.objects.create(
    user=request.user,
    role='Treasurer',
    action='Delete',
    description=f"Deleted donation type: '{donation_type.name}'"
)

    messages.success(request, "Donation type deleted.")
    return redirect('donation_type_list_treasurer')



#LOGOUT


def logout_view(request):
    if 'donor_id' in request.session:
        del request.session['donor_id']
    if request.user.is_authenticated:
        django_logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect('login_register')


from django.utils.timezone import now, timedelta
from django.db.models import Sum
from .models import Donation

def report_view(request):
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    weekly_donations = Donation.objects.filter(date__date__gte=start_of_week)
    monthly_donations = Donation.objects.filter(date__date__gte=start_of_month)

    weekly_total = weekly_donations.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_total = monthly_donations.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'admin_report.html', {
        'weekly_donations': weekly_donations,
        'monthly_donations': monthly_donations,
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
    })

# views.py
from django.shortcuts import render
from .models import Donor
from django.contrib.auth.decorators import login_required, user_passes_test

def is_chairman(user):
    try:
        profile = AdminProfile.objects.get(user=user)
        return profile.role == 'Chairman'
    except AdminProfile.DoesNotExist:
        return False

@user_passes_test(is_chairman)
@login_required
def chairman_activity_logs(request):
    logs = ActivityLog.objects.all().order_by('-timestamp')
    return render(request, 'activity_logs.html', {'logs': logs})

@user_passes_test(is_chairman)
def chairman_donor_list(request):
    donors = Donor.objects.all()
    return render(request, 'donor_list.html', {'donors': donors})


from .models import DonationCategoryRequest, DonationCategory, AdminProfile

@login_required
def review_treasurer_actions(request):
    if not hasattr(request.user, 'adminprofile') or request.user.adminprofile.role != 'Chairman':
        messages.error(request, "Access denied.")
        return redirect('index')

    pending_actions = DonationCategoryRequest.objects.filter(status='pending')

    print("====== DEBUG: PENDING REQUESTS ======")
    for action in pending_actions:
        print(f"ACTION: {action.action} → {action.get_action_display()}")
        print(f"TREASURER: {action.treasurer.user.username}")
        print(f"AFTER: {action.data_after}")
    print("====================================")

    return render(request, 'approve_treasurer.html', {'pending_actions': pending_actions})

from .models import ActivityLog
@login_required
def chairman_activity_logs(request):
    if not hasattr(request.user, 'adminprofile') or request.user.adminprofile.role != 'Chairman':
        messages.error(request, "Access denied.")
        return redirect('index')

    logs = ActivityLog.objects.all().order_by('-timestamp')
    return render(request, 'activity_logs.html', {'logs': logs})

from django.db import IntegrityError

@login_required
def process_request_action(request, request_id, decision):
    if not hasattr(request.user, 'adminprofile') or request.user.adminprofile.role != 'Chairman':
        messages.error(request, "Access denied.")
        return redirect('index')

    category_request = get_object_or_404(DonationCategoryRequest, id=request_id)

    if decision == 'approve':
        if category_request.action == 'create':
            # Check for duplicate name
            if DonationCategory.objects.filter(name=category_request.name).exists():
                messages.error(request, f"Donation type '{category_request.name}' already exists.")
                return redirect('approve_treasurer')

            # Create if no duplicate
            DonationCategory.objects.create(
                name=category_request.name,
                description=category_request.description
            )

        elif category_request.action == 'update' and category_request.original_category:
            category = category_request.original_category

            # Extra check: only update if the new name is not taken OR it's the same record
            if DonationCategory.objects.filter(name=category_request.name).exclude(id=category.id).exists():
                messages.error(request, f"The name '{category_request.name}' is already used by another category.")
                return redirect('approve_treasurer')

            category.name = category_request.name
            category.description = category_request.description
            category.save()

        elif category_request.action == 'delete' and category_request.original_category:
            category_request.original_category.delete()

        category_request.status = 'approved'
        ActivityLog.objects.create(
        user=request.user,
        action='Approved Treasurer Request',
        description=f"{category_request.action.title()} Donation Type: '{category_request.name}'"
    )

    elif decision == 'reject':
        category_request.status = 'rejected'
        ActivityLog.objects.create(
        user=request.user,
        action='Rejected Treasurer Request',
        description=f"{category_request.action.title()} Donation Type: '{category_request.name}' was rejected."
    )

    category_request.save()
    messages.success(request, f"Request has been {category_request.status}.")
    return redirect('approve_treasurer')


# views.py
from collections import defaultdict
from decimal import Decimal
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Donation
import datetime

def download_receipt_pdf(request, donation_id):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        return redirect('login_register')  # user not logged in

    # Get the donation and ensure it belongs to the logged-in donor
    donation = get_object_or_404(Donation, id=donation_id, donor_id=donor_id)

    # Load HTML template for receipt
    template_path = 'donation_receipt_pdf.html'  # create this
    context = {
        'donation': donation,
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{donation.id}.pdf"'

    # Render PDF
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors generating the PDF receipt.')

    return response


@login_required
def annual_report(request):
    selected_month = request.GET.get('month') 
    current_year = timezone.now().year

    # Default
    donations = Donation.objects.filter(date__year=current_year).select_related('donor')
    selected_month_name = None

    if selected_month:
        try:
            year, month = map(int, selected_month.split('-'))
            donations = Donation.objects.filter(date__year=year, date__month=month).select_related('donor')
            selected_month_name = datetime.date(year, month, 1).strftime('%B')
        except:
            pass  # fallback to full year data

    # Group ikut bulan — tapi hanya ikut data yang dipilih (bulan / tahun penuh)
    monthly_data = defaultdict(list)
    for donation in donations:
        month = donation.date.strftime('%B')  # Contoh: 'January', 'February'
        monthly_data[month].append(donation)

    # Semua penderma unik + jumlah
    all_donors = donations.values('donor__donorID', 'donor__donorName')\
        .annotate(total=Sum('amount'))\
        .order_by('-total')

    # Top 3 penderma
    top_donors = all_donors[:3]

    # 💰 Total Donation
    total_donations = donations.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    context = {
        'monthly_data': dict(monthly_data),
        'all_donors': all_donors,
        'top_donors': top_donors,
        'current_year': current_year,
        'total_donations': total_donations,
        'selected_month': selected_month,
        'selected_month_name': selected_month_name,
    }
    return render(request, 'annual_report.html', context)


from collections import defaultdict
from decimal import Decimal
from django.db.models import Sum
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from .models import Donation
from django.conf import settings


@login_required
def generate_pdf(request):
    selected_month = request.GET.get('month')  # e.g. "2025-03"
    current_year = timezone.now().year

    donations = Donation.objects.filter(date__year=current_year).select_related('donor', 'donation_type')
    selected_month_name = None

    if selected_month:
        try:
            year, month = map(int, selected_month.split('-'))
            donations = donations.filter(date__month=month)
            selected_month_name = datetime.date(year, month, 1).strftime('%B')
        except:
            pass  # fallback kalau format salah

    total_donations = donations.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Monthly donation breakdown
    monthly_donations = defaultdict(Decimal)
    for donation in donations:
        month = donation.date.strftime('%B')
        monthly_donations[month] += donation.amount

    # Donation types summary
    donation_type_summary = donations.values('donation_type__name').annotate(total=Sum('amount'))

    # Top donor
    top_donor = donations.values('donor__donorName').annotate(total=Sum('amount')).order_by('-total').first()

    # Largest single donation
    max_donation = donations.order_by('-amount').first()

    # All donors with percentage
    donor_totals = donations.values('donor__donorName').annotate(total=Sum('amount'))
    donor_percentages = []
    for donor in donor_totals:
        percentage = (donor['total'] / total_donations) * 100 if total_donations > 0 else 0
        donor_percentages.append({
            'name': donor['donor__donorName'],
            'total': donor['total'],
            'percentage': round(percentage, 2)
        })

    logo_url = settings.BASE_DIR / 'homepage' / 'static' / 'logo.png'
    logo_path = str(logo_url.resolve())

    template_path = 'pdf_template.html'
    context = {
        'logo_path': logo_path,
        'year': current_year,
        'selected_month': selected_month,
        'selected_month_name': selected_month_name,
        'monthly_donations': dict(monthly_donations),
        'donation_type_summary': donation_type_summary,
        'total_donations': total_donations,
        'top_donor': top_donor,
        'max_donation': max_donation,
        'all_donors': donor_percentages,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    html = get_template(template_path).render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('PDF generation error! <pre>' + html + '</pre>')
    return response

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Donation

@login_required
def view_financial_reports(request):
    user = request.user

    is_chairman = user.username == 'amin'  # tukar ikut actual username
    is_treasurer = user.username == 'hannahbtrisya'  # tukar ikut actual username

    monthly_summary = (
        Donation.objects.filter(status='Approved')
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    donor_totals = (
        Donation.objects.filter(status='Approved')
        .values('donor__donorName')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    type_summary = (
        Donation.objects.filter(status='Approved')
        .values('donation_type__name')
        .annotate(total=Sum('amount'))
    )

    context = {
        'monthly_summary': monthly_summary,
        'type_summary': type_summary,
        'donor_totals': donor_totals,
        'is_chairman': is_chairman,
        'is_treasurer': is_treasurer,
    }

    return render(request, 'financial_reports.html', context)


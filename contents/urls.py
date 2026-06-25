from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_register, name='login_register'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about_page, name='about'),

    # Donor
    path('donor/dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('donor/edit-profile/', views.edit_profile, name='edit_profile'),
    path('make_donation/', views.make_donation, name='make_donation'),
    path('confirm_donation/<int:donation_id>/', views.confirm_donation, name='confirm_donation'),
    path('donation_receipt/<int:donation_id>/', views.donation_receipt, name='donation_receipt'),
    path('donation_history/', views.donation_history, name='donation_history'),
    path('donation-types/', views.donation_type_list_public, name='public_donation_type_list'),
    path('download-receipt/<int:donation_id>/', views.download_receipt_pdf, name='download_receipt'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    # Treasurer
    path('treasurer/dashboard/', views.treasurer_dashboard, name='treasurer_dashboard'),
    path('treasurer/reports/', views.view_financial_reports, name='financial_reports'),
    path('manage_transactions/', views.manage_transactions, name='manage_transactions'),
    path('update-transaction/<int:donation_id>/', views.update_transaction_status, name='update_transaction_status'),

    path('manage-donation-types/', views.donation_type_list_admin, name='donation_type_list_treasurer'),
    path('add-donation-type/', views.add_donation_type, name='add_donation_type'),
    path('edit-donation-type/<int:type_id>/', views.edit_donation_type, name='edit_donation_type'),
    path('delete-donation-type/<int:type_id>/', views.delete_donation_type, name='delete_donation_type'),


    # Chairman
    path('chairman/dashboard/', views.chairman_dashboard, name='chairman_dashboard'),
    path('chairman/donors/', views.chairman_donor_list, name='chairman_donor_list'),
    path('chairman/approve_treasurer/', views.review_treasurer_actions, name='approve_treasurer'),
    path('chairman/activity_logs/', views.chairman_activity_logs, name='activity_logs'),
    path('chairman/annual_report/', views.annual_report, name='annual_report'),
    path('chairman/annual_report/pdf/', views.generate_pdf, name='generate_pdf'),
    path('chairman/treasurer-actions/', views.review_treasurer_actions, name='review_treasurer_actions'),
    path('chairman/requests/<int:request_id>/<str:decision>/', views.process_request_action, name='process_request_action'),


]

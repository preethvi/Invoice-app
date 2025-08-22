from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('invoice/create/', views.create_invoice, name='create_invoice'),
    path('invoice/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:pk>/download/', views.download_invoice_pdf, name='download_invoice_pdf'),
    path('product/add/', views.add_product, name='add_product'),
    path('invoice/<int:pk>/download/', views.download_invoice_pdf, name='download_invoice_pdf'), 
    path('invoices/history/', views.invoice_history, name='invoice_history'),
    path('invoices/search/', views.search_invoices, name='search_invoices'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

]

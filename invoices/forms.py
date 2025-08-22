from django import forms
from .models import Invoice, InvoiceItem, Product

class InvoiceForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Invoice
        fields = ['company', 'client', 'date', 'tax', 'notes']

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity', 'price']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'product_id', 'price']

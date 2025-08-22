from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from .models import Invoice, InvoiceItem, Product
from .forms import InvoiceForm, InvoiceItemForm, ProductForm
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit  # For PDF generation, install pdfkit and wkhtmltopdf
from django.shortcuts import get_object_or_404
from .models import Invoice

def dashboard(request):
    invoices = Invoice.objects.all().order_by('-date')[:5]
    products = Product.objects.all()
    context = {'invoices': invoices, 'products': products}
    return render(request, 'invoices/dashboard.html', context)

def create_invoice(request):
    InvoiceItemFormSet = modelformset_factory(InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True)
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST, queryset=InvoiceItem.objects.none())

        if invoice_form.is_valid() and formset.is_valid():
            invoice = invoice_form.save(commit=False)
            invoice.total = 0
            invoice.save()

            total = 0
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    item = form.save(commit=False)
                    item.invoice = invoice
                    item.save()
                    total += item.get_cost()
            invoice.total = total + invoice.tax
            invoice.save()

            return redirect('invoice_detail', pk=invoice.pk)
    else:
        invoice_form = InvoiceForm()
        formset = InvoiceItemFormSet(queryset=InvoiceItem.objects.none())

    return render(request, 'invoices/create_invoice.html', {
        'invoice_form': invoice_form,
        'formset': formset,
    })

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})

def download_invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    html = render_to_string('invoices/invoice_pdf.html', {'invoice': invoice})

    path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
    pdf = pdfkit.from_string(html, False, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{pk}.pdf"'
    return response

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_invoice')
    else:
        form = ProductForm()
    return render(request, 'invoices/add_product.html', {'form': form})
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Invoice

def download_invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{pk}.pdf"'

    # Setup document with margins
    doc = SimpleDocTemplate(response, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)

    # Use default stylesheet and add centered title style without conflicts
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='CenteredTitle',
                                 parent=styles['Title'],
                                 alignment=1,  # Center
                                 fontSize=18,
                                 spaceAfter=20)

    elements = []

    # Title
    elements.append(Paragraph("Invoice", title_style))

    # Addresses: From (company) and To (client)
    from_address = f"<b>From:</b><br/>{invoice.company.name}<br/>{invoice.company.address.replace('\n', '<br/>')}"
    to_address = f"<b>To:</b><br/>{invoice.client.name}<br/>{invoice.client.address.replace('\n', '<br/>')}"

    address_data = [
        [Paragraph(from_address, styles['Normal']), Paragraph(to_address, styles['Normal'])]
    ]
    address_table = Table(address_data, colWidths=[270, 270])
    elements.append(address_table)
    elements.append(Spacer(1, 20))

    # Invoice items table data
    data = [['Product', 'Quantity', 'Price', 'Cost']]
    for item in invoice.items.all():
        data.append([
            item.product.name,
            str(item.quantity),
            f"${item.price:.2f}",
            f"${item.get_cost():.2f}"
        ])

    # Add tax and grand total rows
    data.append(['', '', 'Tax', f"${invoice.tax:.2f}"])
    data.append(['', '', 'Grand Total', f"${invoice.total:.2f}"])

    table = Table(data, colWidths=[250, 70, 100, 100])

    # Styling the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 1), (-1, -3), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

        ('SPAN', (0, -2), (2, -2)),  # Span Tax label across 3 columns
        ('ALIGN', (0, -2), (2, -2), 'RIGHT'),
        ('SPAN', (0, -1), (2, -1)),  # Span Grand Total label across 3 columns
        ('ALIGN', (0, -1), (2, -1), 'RIGHT'),

        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ])
    table.setStyle(style)

    elements.append(table)

    # Build the PDF into the response
    doc.build(elements)

    return response
# invoices/views.py
from django.shortcuts import render

def invoice_history(request):
    # Your logic here
    return render(request, 'invoices/history.html', {})

# invoices/views.py
from django.shortcuts import render
from .models import Invoice  # or your model

def search_invoices(request):
    query = request.GET.get('q', '')
    results = Invoice.objects.filter(client__name__icontains=query) if query else []
    return render(request, 'invoices/search_results.html', {'invoices': results, 'query': query})
# your_app/views.py
from django.shortcuts import render

def profile_view(request):
    # Your user profile logic here
    return render(request, 'your_app/profile.html')

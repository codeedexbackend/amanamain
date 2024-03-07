# utils.py

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  # Make sure to install the xhtml2pdf library
from django.utils import timezone


def generate_bill_number(model):
    # Get the current year and month
    year_month = timezone.now().strftime('%Y%m')

    # Count existing orders with the same year and month
    existing_orders_count = model.objects.filter(bill_number__startswith=f'AMANA-{year_month}-').count()

    # Format the bill number with the prefix and counter
    return f'AMANA-{year_month}-{existing_orders_count + 1:03d}'

def render_to_pdf(template_path, context_dict):
    template = get_template(template_path)
    html = template.render(context_dict)
    result = BytesIO()

    # Create a PDF file
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

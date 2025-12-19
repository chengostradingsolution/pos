from num2words import num2words

def amount_in_words(amount):
    """
    Converts number to Indian currency words
    Example: 1234.50 -> Rupees One Thousand Two Hundred Thirty Four and Fifty Paise Only
    """
    amount = float(amount)
    rupees = int(amount)
    paise = int(round((amount - rupees) * 100))

    words = f"Rupees {num2words(rupees, lang='en_IN').title()}"

    if paise > 0:
        words += f" and {num2words(paise, lang='en_IN').title()} Paise"

    return words + " Only"



from datetime import date
from django.db.models import Max
from .models import Sales

def generate_invoice_number():
    today = date.today()
    fy_start = today.year if today.month >= 4 else today.year - 1
    fy_end = fy_start + 1
    fy = f"{fy_start}-{str(fy_end)[-2:]}"  # 2025-26

    prefix = f"CTS/{fy}/"

    last_invoice = Sales.objects.filter(
        code__startswith=prefix
    ).aggregate(Max('code'))['code__max']

    if last_invoice:
        last_number = int(last_invoice.split('/')[-1])
        next_number = last_number + 1
    else:
        next_number = 1

    return f"{prefix}{next_number:06d}"

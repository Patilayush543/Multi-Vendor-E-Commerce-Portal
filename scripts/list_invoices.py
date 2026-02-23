from myapp.models import Invoice
ins = Invoice.objects.all()
print('INVOICE_COUNT=', ins.count())
for inv in ins:
    orders = list(inv.orders.values_list('id', flat=True))
    users = list(set(o.user.username for o in inv.orders.all()))
    print(inv.id, inv.invoice_number, float(inv.total), orders, users)

{
    'name': "Método de Pagamento Zoop",
    'summary': "Payment Acquirer: Zoop",
    'description': """Zoop payment gateway for Odoo.""",
    'author': "Danimar Ribeiro",
    'category': 'Accounting',
    'version': '13.0.1.0.0',
    'depends': ['l10n_br_automated_payment', 'payment', 'sale'],
    'data': [
        'views/payment_views.xml',
        'views/zoop.xml',
        'views/account_journal.xml',
        'views/templates.xml',
        'data/zoop.xml',
    ],
    'application': True,
}

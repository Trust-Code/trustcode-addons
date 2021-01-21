{  # pylint: disable=C8101,C8103
    'name': 'CRM Customização para cobranças',
    'version': '13.0.1.0.0',
    'category': 'account',
    'author': 'Trustcode',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'sale_crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/lead.xml',
        'views/negotiation.xml',
        'views/sale_order.xml',
        'views/res_partner.xml',
        'views/sale_templates.xml',
    ],
}
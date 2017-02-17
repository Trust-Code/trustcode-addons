# -*- coding: utf-8 -*-
# © 2015 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Trustcode - Agrupador de Serviço',
    'description': 'Agrupador de serviços',
    'summary': """
        - Controla de um local unico todas as ordens de serviço.
    """,
    'version': '10.0.1.0.0',
    'category': 'MRP',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'sale', 'mrp', 'crm', 'purchase', 'account', 'asset', 'mro'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mro_group.xml',
        'views/crm_lead.xml',
        'views/sale_order.xml',
        'views/account_invoice.xml',
        'views/stock_picking.xml',
        'views/purchase.xml',
        'views/mro.xml',
    ],
    'application': False,
}

# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Trust Correios",
    'summary': """Integração com os Correios""",
    'description': """Módulo para gerar etiquetas de rastreamento de \
encomendas""",
    'version': '10.0.1.0.0',
    'category': 'MRP',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Alessandro Fernandes Martini <alessandrofmartini@gmail.com>'
    ],
    'depends': [
        'stock', 'delivery'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/delivery_carrier.xml',
        'views/sale_order.xml',
        'views/product_template.xml',
        'views/stock_picking.xml',
        'reports/shipping_label.xml',
        'reports/plp_report.xml',
    ],
    'application': True,
    'instalable': False,
}

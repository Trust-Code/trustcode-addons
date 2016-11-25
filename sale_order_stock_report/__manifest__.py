# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Modelo de Cotação de Venda Stock',
    'description': "Modelo de Cotação de Venda Stock",
    'summary': "Modelo de Cotação de Venda Stock",
    'version': '10.0.1.0.0',
    'category': "Sales",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>'
    ],
    'depends': [
        'sale_order_report', 'sale_stock',
    ],
    'data': [
        'reports/sale_order.xml',
    ],
    'auto_install': True,
}

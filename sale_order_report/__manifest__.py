# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Modelo de Cotação de Venda',
    'description': "Modelo de Cotação de Venda",
    'summary': "Modelo de Cotação de Venda",
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
        'base_report', 'sale', 'br_account',
    ],
    'data': [
        'reports/sale_order.xml',
    ],
}

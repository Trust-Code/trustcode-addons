# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Cash Flow Report - Forecast Orders',
    'summary': """Add confirmed sales order to cash flow""",
    'version': '8.0.1.0.0',
    'category': 'Tools',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'sale', 'sale_order_dates', 'account_cash_flow'
    ],
    'data': [
        'views/cash_flow_view.xml'
    ],
}

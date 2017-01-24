# -*- coding: utf-8 -*-
# © 2015 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Trustcode - Invoice to third party',
    'description': 'Invoice the sales order to a third party',
    'summary': """
        Invoice the sales order to a third party
    """,
    'version': '10.0.1.0.0',
    'category': 'Invoicing & Payments',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'br_sale', 'br_account'
    ],
    'data': [
        'views/res_partner.xml',
        'views/account_invoice.xml',
    ],
}

# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': 'Trustcode - Rules do invoice sales order',
    'description': 'You can create rules to generate invoices from sale order',
    'summary': """
        You can create rules to generate invoices from sale order
    """,
    'version': '10.0.1.0.0',
    'category': 'Invoicing',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'sale',
        'sale_order_contract',
        'account',
        'mail',
    ],
    'data': [
        'views/res_partner.xml',
        'views/account_fiscal_position_view.xml',
        'views/mail_template.xml'
    ],
}

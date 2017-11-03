# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': "invoice_dollar2real",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Uncategorized',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [

    ],
    'depends': ['base', 'account', 'sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}

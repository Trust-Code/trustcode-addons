# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy <johnychenjy@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{   # pylint: disable=C8101,C8103
    'name': 'Update Invoice Line Taxes',
    'summary': """Updates Invoice Line Taxes""",
    'version': '11.0.1.0.0',
    'category': 'NFE',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Johny Chen Jy <johnychenjy@gmail.com>',
    ],
    'depends': [
        'br_account',
    ],
    'data': [
        'views/account_invoice_views.xml'
    ],
}

# -*- coding: utf-8 -*-
# © 2018, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{   # pylint: disable=C8101,C8103
    'name': 'Account Asset - addon',
    'description': "Add asset number column in tree view",
    'summary': """  """,
    'version': '10.0.1.0.0',
    'category': 'Uncategorized',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Marina Domingues <marina.domingues@gmail.com>',
    ],
    'depends': [
        'account_asset', 'asset_account'
    ],
    'data': [
        'views/asset_view.xml',
    ],
}

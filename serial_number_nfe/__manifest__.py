# -*- coding: utf-8 -*-
# © 2015 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Trustcode - Add Serial Number to Invoice Eletronic',
    'description': 'Add Serial Number to Invoice Eletronic',
    'summary': """
        Add Serial Number to Invoice Eletronic (NFe)
        It needs some special configuration like:
         - invoice only delivered quantities
    """,
    'version': '10.0.1.0.0',
    'category': 'Stock',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'br_nfe', 'sale_stock', 'product_expiry'
    ],
    'data': [],
}

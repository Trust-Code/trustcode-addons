# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{   # pylint: disable=C8101,C8103
    'name': "Purchase Uom",

    'summary': """
        Permite adicionar uma segunda unidade de compra, mesmo que esta não
        pertença à mesma categoria das outras unidades.""",

    'description': """""",
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    'depends': ['purchase'],
    'data': [
        'views/supplier_info.xml',
        'views/purchase_order.xml',
    ],
}
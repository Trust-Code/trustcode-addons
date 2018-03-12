# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': "Fluxo de Compras GML",

    'summary': """
        Ajuste do fluxo de Compras para empresa GML""",

    'description': """""",
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Purchase',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    'depends': ['purchase'],
    'data': [
        'views/purchase_order.xml',
    ],
}

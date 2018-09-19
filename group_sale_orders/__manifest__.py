# -*- coding: utf-8 -*-
# © Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': "Agrupar Cotações",

    'summary': """Permite o agrupamento de cotações que contenham
    mesma empresa, parceiro e posição fiscal.
    """,

    'description': """""",

    'category': 'Sales',
    'version': '10.0.1.0.0',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    'depends': ['sale'],

    'data': [
        'views/sale_order.xml',
    ],
}

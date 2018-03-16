# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{   # pylint: disable=C8101,C8103
    'name': "Fluxo de Design para Vendas",

    'summary': """
        Insere estágio de Design em uma venda, antes da confirmação
        da venda.""",

    'description': """
    """,
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Sale',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    'depends': ['sale_timesheet'],
    'data': [
        'views/sale_order.xml',
        'views/product.xml',
    ],
}

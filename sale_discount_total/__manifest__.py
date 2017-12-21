# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': "Desconto total",

    'summary': """
        Aplica desconto sobre o total da venda.""",

    'description': """
        Desconto sobre o total da venda, o desconto pode ser do tipo
        percentual ou uma quantia específica para ser descontada do
        total bruto da venda.
    """,
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [],
    'depends': ['sale'],
    'data': [
        'views/sale_order_view.xml'
    ],
}

# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Product Special Fields',
    'description': "Campos adicionais para controle de stock",
    'summary': """"Campos adicionais configuráveis no produto, permitindo inserir
o valor do IMEI, ICCID, No linha""",
    'version': '11.0.1.0.0',
    'category': "stock",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Johny Chen Jy <johnychenjy@gmail.com>',
    ],
    'depends': [
        'stock',
        'product',
    ],
    'data': [
        'views/product_template_views.xml',
        'views/stock_production_lot_views.xml',
        'views/stock_move_line_views.xml',
    ],
}

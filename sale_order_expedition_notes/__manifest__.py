# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': "Expedition Notes for Sale Orders",
    'summary': """
        Enables Sale Order Expedition Notes which are transfered to
        respective stock.move""",
    'description': """""",
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Sale',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Johny Chen Jy <johnychenjy@gmail.com>'],
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
    ],
}

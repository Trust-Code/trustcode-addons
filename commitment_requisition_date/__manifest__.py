# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy <>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{   # pylint: disable=C8101,C8103
    'name': 'Picking and MRP Commitment and Requisition Dates',
    'description': "\
        Commitment and Requisition Dates for stock.picking and mrp.production",
    'version': '11.0.1.0.0',
    'category': "Administration",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Johny Chen Jy <johnychenjy@gmail.com>',
    ],
    'depends': [
        'sale',
        'mrp',
        'stock',
        'sale_order_dates',
    ],
    'data': [
        'views/mrp_production_view.xml',
        'views/stock_picking_view.xml',
        'views/sale_order_view.xml',
    ],
}

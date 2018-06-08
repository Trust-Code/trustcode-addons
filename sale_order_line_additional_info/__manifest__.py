# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': "Sale Order Line Additional Info",
    'summary': """
        Additional information in sale.order.lines which are \
transfered to manufacture order.""",
    'description': """""",
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Sale',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Johny Chen Jy <johnychenjy@gmail.com>'],
    'depends': [
        'sale',
        'product_configurator',
        ],
    'data': [
        'views/sale_order_line_views.xml',
        'views/mrp_production_view.xml',
        'wizard/additional_info_wizard_view.xml',
    ],
}

# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': "stock_delivery_info",

    'summary': """
        Envia as informações de transporte, necessárias para a emissão
        de uma NF-e, com base no picking de entrega.""",
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Fábio Luna <fabiocluna@hotmail.com>',
    ],
    'depends': [
        'base',
        'stock_json_api',
    ],
    'data': [
        'views/res_config_settings.xml',
        'views/stock_picking_type.xml',
    ],
}

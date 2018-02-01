# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Control Stock via API',
    'description': "Control Stock via API",
    'summary': "Control the incoming",
    'version': '11.0.1.0.0',
    'category': "stock",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'stock', 'br_zip',
    ],
    'data': [
        'views/res_users.xml',
        'views/res_config_settings.xml',
        'views/stock.xml',
        'views/stock_picking.xml',
    ],
}

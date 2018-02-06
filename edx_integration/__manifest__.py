# -*- coding: utf-8 -*-
# © 2018 Fábio Luna
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{   # pylint: disable=C8101,C8103
    'name': 'EDX Integration',
    'description': "Módulo para integrar Odoo ao Open EDX",
    'version': '11.0.1.0.0',
    'category': "Administration",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Fábio Luna <fabiocluna@hotmail.com>',
    ],
    'depends': [
        'br_base',
        'mail',
    ],
    'data': [
        'data/edx_data.xml',
        'wizard/edx_wizard_view.xml',
        'views/res_config_settings.xml',
    ],
}

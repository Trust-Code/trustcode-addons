# -*- coding: utf-8 -*-
{
    'name': 'Apps Actions History',
    'version': '1.0',
    'summary': """Displaying History of module installation/uninstallation/upgradation""",
    'description': """History of module installation/uninstallation/upgradation""",
    'category': 'Base',
    'author': 'bisolv',
    'website': "",
    'license': 'AGPL-3',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'views/ir_module_history_view.xml',
    ],
    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'qweb': [],

    'installable': True,
    'auto_install': False,
    'application': False,
}

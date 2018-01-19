# -*- coding: utf-8 -*-
# Copyright 2016, 2017 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{   # pylint: disable=C8101,C8103,C7902
    "name": "Material/United Backend Theme",
    "summary": "Odoo 11.0 community backend theme",
    "version": "11.0.1.0.2",
    "category": "Themes/Backend",
    "website": "http://www.openworx.nl",
    "description": """
        Backend theme for Odoo 11.0 community edition.
    """,
    'images': [
        'images/screen.png'
    ],
    "author": "Openworx",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        'web_responsive',
    ],
    "data": [
        'views/assets.xml',
        'views/res_company_view.xml',
        'views/users.xml',
        'views/sidebar.xml',
    ],
}

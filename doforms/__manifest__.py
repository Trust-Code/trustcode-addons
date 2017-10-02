# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'doforms',
    'author': 'Mackilem Van der Laan',
    'version': '1.0',
    'category': '',
    'sequence': 5,
    'summary': '',
    'description': """

====================================================

""",
    'website': 'https://www.trustcode.com.br',
    'depends': ['mail', 'project'],
    'data': ['views/doforms.xml',
             'data/ir_sequence.xml',
             'security/security.xml',
             'security/ir.model.access.csv'
             ],
    'installable': True,
    'application': False,
    'auto_install': False,
    }

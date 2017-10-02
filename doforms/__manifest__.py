# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{   # pylint: disable=C8101,C8103
    'name': 'Formulário Base',
    'description': "",
    'summary': "",
    'version': '10.0.1.0.0',
    'category': "",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>'
    ],
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

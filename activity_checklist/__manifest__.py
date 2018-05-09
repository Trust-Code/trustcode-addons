# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{   # pylint: disable=C8101,C8103
    'name': "Checklist de Atividades",

    'summary': """
        Módulo para a criação de um checklist para as atividades""",

    'description': """""",
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    'depends': ['mail', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/activity_checklist.xml',
        'views/project.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}

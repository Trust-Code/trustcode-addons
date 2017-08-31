# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Issue Satisfaction Survey',
    'version': '1.0',
    'category': '',
    'sequence': 5,
    'summary': 'Pesquisa de satisfação em tarefas',
    'description': """

====================================================

""",
    'website': 'https://www.trustcode.com.br',
    'depends': ['project_issue',],
    'data': [
        'wizard/project_issue.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

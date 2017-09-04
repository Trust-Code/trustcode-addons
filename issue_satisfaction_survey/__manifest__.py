# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Issue Satisfaction Survey',
    'version': '10.0.1.0.0',
    'category': 'Project',
    'summary': 'Pesquisa de satisfação em tarefas',
    'description': "Pesquisa de satisfação em tarefas",
    'website': 'https://www.trustcode.com.br',
    'depends': ['project_issue'],
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'data': [
        'views/project_issue.xml',
        'wizard/project_issue_close.xml',
    ],
}

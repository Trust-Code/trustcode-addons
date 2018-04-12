# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'ProjectSLA',
    'version': '10.0.1.0.0',
    'category': '',
    'sequence': 5,
    'summary': '',
    'license': 'AGPL-3',
    'description': """

====================================================

""",
    'website': 'https://www.trustcode.com.br',
    'depends': [
        'project_issue',
    ],
    'data': [
        'views/project_issue.xml',
        'views/project_task_type.xml'
    ],
    'installable': True,
}

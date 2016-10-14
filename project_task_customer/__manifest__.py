# -*- coding: utf-8 -*-
# © 2015 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Trustcode - Customer and tasks',
    'description': 'Small improvements to tasks and issues',
    'summary': """
        - Add partner logo to kanban
    """,
    'version': '10.0.1.0.0',
    'category': 'Project',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'project', 'project_issue'
    ],
    'data': [
        'views/project.xml',
    ],
    'auto_install': True,
}

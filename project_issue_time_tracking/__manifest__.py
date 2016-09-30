# -*- coding: utf-8 -*-
# © 2015 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Controle de tempo nos incidentes',
    'description': 'Controle de tempo nos incidentes',
    'summary': """Automatiza a contagem de tempo nos incidentes
    de acordo com o estágio""",
    'version': '10.0.1.0.0',
    'category': 'Project',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'project_issue_sheet',
        'project_task_time_tracking'
    ],
    'data': [
        'views/project_issue_view.xml',
    ],
}

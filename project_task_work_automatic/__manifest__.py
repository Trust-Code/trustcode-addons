# -*- coding: utf-8 -*-
# © 2015 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Controle de tempo das Tarefas',
    'description': 'Controle de tempo das Tarefas',
    'summary': """Automatiza a contagem de tempo nas tarefas
    de acordo com o estágio""",
    'version': '10.0.1.0.0',
    'category': 'Project',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>'
    ],
    'depends': [
        'project', 'hr_timesheet'
    ],
    'data': [
        'views/project_task_view.xml',
    ],
}

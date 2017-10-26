# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Materiais em Tarefas',
    'description': "Materiais em Tarefas",
    'summary': "Materiais em Tarefas",
    'version': '10.0.1.0.0',
    'category': "Taks",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>'
    ],
    'depends': [
        'project',
        'stock',
        'sale_timesheet'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/task_materials.xml',
    ],
}

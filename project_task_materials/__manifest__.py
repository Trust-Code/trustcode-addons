# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'List of Materials in Task',
    'description': "List of Materials in Task",
    'summary': "List of Materials in Task",
    'version': '11.0.1.0.0',
    'category': "Taks",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>',
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    'depends': [
        'project',
        'stock',
        'sale_timesheet'
    ],
    'data': [
        'data/picking_type.xml',
        'security/ir.model.access.csv',
        'views/project_task_materials.xml',
        'views/project_task.xml',
    ],
}

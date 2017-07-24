# -*- coding: utf-8 -*-
# © 2017 Fillipe Ramos, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Report de Comissões',
    'description': "Report de Comissões",
    'summary': "Report de Comissões",
    'version': '10.0.1.0.0',
    'category': "Report",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>'
    ],
    'depends': [
        'base_report',
        'royalties',
        'account',
    ],
    'data': [
        'reports/royalties_report.xml',
    ],
}

# -*- coding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{   # pylint: disable=C8101,C8103
    'name': 'Relatório de Royalties',
    'description': "Report de Comissões",
    'summary': "Report de Comissões",
    'version': '10.0.1.0.0',
    'category': "Report",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>',
        'Fábio Luna <fabiocluna@hotmail.com>'
    ],
    'depends': [
        'base_report',
        'royalties',
        'account',
    ],
    'data': [
        'reports/royalties_report.xml',
        'reports/synthetic_royalties_report.xml',
    ],
}

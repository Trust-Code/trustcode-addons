# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Base de Relatórios da Trustcode',
    'description': "Modifica o footer e o cabeçalho padrão de documentos",
    'version': '10.0.1.0.0',
    'category': "Administration",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'sale', 'br_account',
    ],
    'data': [
        'reports/base_report.xml',
    ],
}

# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Nota de Débito',
    'description': "Nota de Débito Odoo",
    'summary': "Layout de Nota de Débito Simples do Odoo",
    'version': '11.0.1.0.0',
    'category': "account",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'br_account',
    ],
    'data': [
        'reports/nota_debito.xml',
    ],
}

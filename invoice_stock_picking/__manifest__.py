# -*- coding: utf-8 -*-
# © 2017 Fábio Luna <fabiocluna@hotmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{   # pylint: disable=C8101,C8103
    'name': 'Fatura Gera Picking',
    'version': '10.0.1.0.0',
    'category': 'Account addons',
    'license': 'OPL-1',
    'author': 'Trustcode',
    'website': 'http://www.trustcode.com.br',
    'description': """
        Cria movimento de estoque a partir de uma fatura com base na posição
         fiscal.""",
    'contributors': [
        'Fábio Luna <fabiocluna@hotmail.com>',
    ],
    'depends': [
        'br_account',
        'stock',
    ],
    'data': [
        'views/account_fiscal_position.xml',
    ],
    'installable': True,
}

# -*- coding: utf-8 -*-
# © 2017 Felipe Paloschi <paloschi.eca@gmail.com>, Trustcode
# © 2017 Johny Chen Jy <johnychenjy@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': "Faturamento em BRL",
    'summary': """
        Fixa o faturamento no Odoo em reais""",
    'description': """
        Ao criar a fatura sempre modifica a moeda para reais.
    """,
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Uncategorized',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Felipe Paloschi <paloschi.eca@gmail.com>',
        'Johny Chen Jy <johnychenjy@gmail.com>',
        'Fabio Luna <fabiocluna@hotmail.com>'
    ],
    'depends': [
        'account', 'sale'
    ],
}

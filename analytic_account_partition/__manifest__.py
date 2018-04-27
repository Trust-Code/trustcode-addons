# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': "Rateio entre Contas Analíticas",

    'summary': """
        Rateio de custos entre contas analíticas""",

    'description': """
    """,
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Accounting & Finance',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    'depends': ['br_account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'views/analytic_partition.xml',
        'views/analytic_account.xml'
    ],
}

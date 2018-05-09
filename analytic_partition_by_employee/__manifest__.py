# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': "Rateio de custos por funcionário",

    'summary': """
        Configura o rateio de custos de acordo com a
        quantidade de funcionários relacionadas a cada centro
        de custo.""",

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
    'depends': [
        'analytic_account_partition', 'hr', 'account_voucher'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/res_partner.xml',
        'views/account_move.xml',
        'views/account_voucher.xml',
        'views/analytic_account.xml',
    ],
}

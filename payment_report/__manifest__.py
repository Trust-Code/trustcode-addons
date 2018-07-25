# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Relatório para Pagamentos',
    'description': "Layout para relatório simples de pagamentos",
    'summary': "Layout para relatório simples de pagamentos",
    'version': '10.0.1.0.0',
    'category': "Accounting & Finance",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Johny Chen Jy <johnychenjy@gmail.com>'
    ],
    'depends': [
        'account',
    ],
    'data': [
        'reports/account_payment_reports.xml',
        'views/account_payment_views.xml',
    ],
}

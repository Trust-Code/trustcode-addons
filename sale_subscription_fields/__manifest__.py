# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sales Subscription Fields',
    'summary': """Módulo que cria campos adicionais no módulo de contratos.""",
    'description': "Campos Adicionais em Sale Subscription",
    'version': '11.0.1.0.0',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': ['Johny CHen Jy <johnychenjy@gmail.com>'
                     ],
    'depends': [
        'sale_subscription',
    ],
    'data': [
        'views/monetary_adjustment_ratio.xml',
        'views/sale_subscription_view.xml',
        'security/ir.model.access.csv',
    ],
}

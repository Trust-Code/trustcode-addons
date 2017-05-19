# -*- coding: utf-8 -*-
# © 2015 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Trustcode - Contratos recorrentes',
    'description': 'Contratos via pedido de Venda',
    'summary': """
        - Gerencia contratos recorrentes através de um pedido de venda
    """,
    'version': '10.0.1.0.0',
    'category': 'Sales',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'sale', 'account', 'sale_margin', 'br_account_payment'
    ],
    'data': [
        'data/admin_contract_active.xml',
        'data/payment_term.xml',
        'data/ir_cron.xml',
        'views/sale_order_contract.xml',
        'views/sale_order.xml',
        'views/product.xml',
        'views/payment_term.xml',
        'wizard/sale_contract_renew.xml',
        'data/admin_contract_active.xml',
    ],
    'application': True,
}

# -*- coding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Atualização da Receita Recorrente',
    'description': "Realiza a atualização da receita recorrente ao gravar "
                   " cotação",
    'version': '10.0.1.0.0',
    'category': "Customization",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Fábio Luna<fabiocluna@hotmail.com>',
    ],
    'depends': [
        'sale',
        'sale_crm',
        'sale_order_contract'
    ],
    'data': [
        'views/sale_order.xml',
        'views/crm_lead.xml',
        'views/crm_lead_kanban.xml',
    ],
    'application': True,
    'installable': True,
}

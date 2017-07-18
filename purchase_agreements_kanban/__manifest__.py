# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Agreements Advanced kanban',
    'version': '1.0',
    'category': 'Purchases',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'description': """
Insere um novo kanban para controle avançado de compras
    """,
    'website': 'www.trustcode.com.br',
    'depends': ['purchase_requisition'],
    'data': [
        'views/purchase_advanced_kanban.xml',
    ],
    'installable': True,

}

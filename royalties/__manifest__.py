# -*- coding: utf-8 -*-
# © 2017 Fillipe Ramos, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Pagamento de Royalties',
    'description': "Pagamento de Royalties",
    'summary': "Pagamento de Royalties",
    'version': '10.0.1.0.0',
    'category': "account",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>'
    ],
    'depends': [
        'product',
        'sale',
        'account',
        'account_voucher',
    ],
    'data': [
        'views/product.xml',
        'views/res_partner.xml',
        'views/royalties.xml',
        'views/account_voucher.xml',
        'views/fiscal_position.xml',
        'views/account_journal.xml',
        'wizard/royalties.xml',
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}

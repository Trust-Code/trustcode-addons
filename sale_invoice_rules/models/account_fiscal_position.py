# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    documento_produto_id = fields.Many2one('br_account.fiscal.document',
                                           'Documento Produtos')
    documento_nota_servico_id = fields.Many2one('br_account.fiscal.document',
                                                'Documento Nota de Serviço')
    documento_nota_debito_id = fields.Many2one('br_account.fiscal.document',
                                               'Documento Nota de Débito')

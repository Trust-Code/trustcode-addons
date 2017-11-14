# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    branch_id = fields.Many2one('res.partner', string="Matriz")
    branch_ids = fields.One2many('res.partner', 'branch_id', string="Filiais")
    percentual_nota_debito = fields.Float(string="% Nota débito")
    percentual_faturamento = fields.Float(string="Percentual Faturamento")

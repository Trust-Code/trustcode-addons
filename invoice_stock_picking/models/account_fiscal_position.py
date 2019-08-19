# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class FiscalPosition(models.Model):

    _inherit = ['account.fiscal.position']

    picking_type_id = fields.Many2one(
        'stock.picking.type', string=u'Tipo de Separação')

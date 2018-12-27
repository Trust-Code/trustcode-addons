# -*- coding: utf-8 -*-
# © 2018, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    entregador_id = fields.Many2one(
        comodel_name='res.partner',
        string="Responsável pela entrega",
        domain=[('entregador', '=', True)])

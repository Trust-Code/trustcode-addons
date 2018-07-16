# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    commitment_date = fields.Datetime(
        'Data do Compromisso', track_visibility='onchange')
    requisition_date = fields.Datetime(
        'Data do Requisição', track_visibility='onchange')
    observation_order_sale = fields.Text(
        'Observation')

# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from datetime import datetime, time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    kk_date_planned = fields.Date(string="Data Programada")

    @api.onchange("kk_date_planned")
    def _onchange_kk_date_planned(self):
        for item in self:
            if item.kk_date_planned:
                item.date_planned = datetime.combine(
                    datetime.strptime(item.kk_date_planned, DF), time(15)
                )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    kk_site_id = fields.Many2one("kk.sites", string="Site")
    kk_site_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente Site",
        related="kk_site_id.partner_id",
    )
    kk_date_planned = fields.Date(string="Data Programada")
    kk_delivery_date = fields.Date(string="Data de Entrega")

    @api.onchange("kk_date_planned")
    def _onchange_kk_date_planned(self):
        for item in self:
            if item.kk_date_planned:
                item.date_planned = datetime.combine(
                    datetime.strptime(item.kk_date_planned, DF), time(15)
                )

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

    @api.multi
    def action_set_date_planned(self):
        super(PurchaseOrder, self).action_set_date_planned()
        for order in self:
            order.order_line.update(
                {"kk_date_planned": order.kk_date_planned}
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
    kk_site_city_state = fields.Char(
        string="Cidade/UF", compute="_compute_kk_site_city_state", store=True
    )

    @api.multi
    @api.depends("kk_site_id")
    def _compute_kk_site_city_state(self):
        for item in self:
            item.kk_site_city_state = (
                "{}/{}".format(
                    item.kk_site_id.city_id.name,
                    item.kk_site_id.state_id.code,
                )
                if item.kk_site_id
                else ""
            )

    @api.onchange("kk_date_planned")
    def _onchange_kk_date_planned(self):
        for item in self:
            if item.kk_date_planned:
                item.date_planned = datetime.combine(
                    datetime.strptime(item.kk_date_planned, DF), time(15)
                )

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrderLine, self).write(vals)
        if vals.get("kk_delivery_date"):
            for item in self:
                item.order_id.message_post(
                    body="Data de entrega do produto {} definida para {}".format(
                        item.product_id.name,
                        datetime.strptime(item.kk_delivery_date, DF).strftime(
                            "%d/%m/%Y"
                        ),
                    )
                )
        return res

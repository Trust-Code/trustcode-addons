
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_usd_price(self):
        brl_id = self.env['res.currency'].search([('name', '=', 'BRL')])
        usd_id = self.env['res.currency'].search([('name', '=', 'USD')])
        for item in self:
            item.brl_currency_id = usd_id.id
            item.brl_amount_total = brl_id.compute(item.amount_total, usd_id)

    brl_currency_id = fields.Many2one('res.currency', compute="_compute_usd_price")
    brl_amount_total = fields.Monetary(currency="brl_currency_id", compute="_compute_usd_price")
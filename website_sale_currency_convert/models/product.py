
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _compute_brl_price(self):
        brl_id = self.env['res.currency'].search([('name', '=', 'BRL')])
        usd_id = self.env['res.currency'].search([('name', '=', 'USD')])
        for item in self:
            dolar_price = item.item_ids.filtered(lambda x: x.currency_id == usd_id)
            item.brl_currency_id = usd_id.id
            if dolar_price:
                item.brl_list_price = dolar_price.fixed_price
            else:
                item.brl_list_price = 0.0

    brl_currency_id = fields.Many2one('res.currency', compute="_compute_brl_price")
    brl_list_price = fields.Monetary(currency="brl_currency_id", compute="_compute_brl_price")
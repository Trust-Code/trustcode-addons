
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _compute_brl_price(self):
        brl_id = self.env['res.currency'].search([('name', '=', 'USD')])
        for item in self:
            item.brl_currency_id = brl_id.id
            item.brl_list_price = brl_id.compute(item.list_price, brl_id)

    brl_currency_id = fields.Many2one('res.currency', compute="_compute_brl_price")
    brl_list_price = fields.Monetary(currency="brl_currency_id", compute="_compute_brl_price")
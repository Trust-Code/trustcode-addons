
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        res = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty, pricelist, parent_combination, only_template)

        brl_id = self.env['res.currency'].search([('name', '=', 'BRL')], limit=1)
        usd_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        res["usd_list_price"] = brl_id.compute(res['price'], usd_id)
        return res
import time
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api


class Sale_pricelist_simple_view_product(models.Model):
    _inherit = 'product.template'

    lines_prices_id = fields.One2many('product.pricelist.line', 'product_id', 'Lista')
    tag_id_sale = fields.Many2many('product.pricelist.line', domain="[['product_id','=', id]]", string="Listas de Preço")

    def get_scale_list(self):
        line_tags = self.env['product.pricelist.line'].search(['&', ('pricelist_ids.show_list', '=', True), ('product_id.id', '=', self.id)])
        self.tag_id_sale.unlink()
        self.tag_id_sale = line_tags

    def change_pricelist(self):
        product_id = self.env[
            'product.template'].search([('id', '=', self.id)], limit=1)
        list_prices = self.env[
            'product.pricelist'].search([('show_list', '=', True)])
        prices = []
        for l in list_prices:
            price = product_id.with_context(pricelist=l.id).price

            prices.append((0, 0, {
                        'product_id': self.id,
                        'pricelist_ids': l.id,
                        'price_required': price,
                        'show_list': l.show_list,
                        'color': l.color_id.color}))

            product_id.invalidate_cache(ids=[product_id.id])

        self.lines_prices_id.unlink()
        self.lines_prices_id = prices
        self.get_scale_list()

    def change_pricelist_cron(self):
        product_id = self.env['product.template'].search([])
        for l in product_id:
            l.change_pricelist()

    def copy(self, default=None):
        new = super(
            Sale_pricelist_simple_view_product, self).copy(default=default)
        copies_ids = []
        for line in self.lines_prices_id:
            copies_ids.append(line.copy(default=default).id)
        self.write({'lines_prices_id': [(6, False, copies_ids)]})
        return new

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    applied_on = fields.Selection(selection_add=[('4_fiscal_category', 'Categoria Fiscal')],
                                  ondelete={'4_fiscal_category': 'set default'}, default="3_global")
    # applied_on = fields.Selection(selection_add=[('4_fiscal_category', 'Categoria Fiscal')])
    fiscal_category = fields.Many2one(
        'product.fiscal.category', string='Categoria Fiscal do Produto', ondelete='cascade'
    )

    @api.constrains('product_id', 'product_tmpl_id', 'categ_id')
    def _check_product_consistency(self):
        for item in self:
            if item.applied_on == "4_fiscal_category" and not item.fiscal_category:
                raise ValidationError("Por favor especifique a categoria fiscal em qual essa regra será aplicada")
        super(PricelistItem, self)._check_product_consistency()

    @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price',
                 'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _get_pricelist_item_name_price(self):
        super(PricelistItem, self)._get_pricelist_item_name_price()
        for item in self:
            if item.fiscal_category and item.applied_on == '4_fiscal_category':
                item.name = "Categoria Fiscal: %s" % (item.fiscal_category.name)

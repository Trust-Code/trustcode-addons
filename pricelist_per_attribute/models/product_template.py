

from odoo import api, fields, models


class ProductAttributeValuePrice(models.Model):
    _name = 'product.attribute.value.price'
    _description = 'Cria uma tabela de preco quantidade por atributo'
    _order = "min_quantity"

    min_quantity = fields.Float(string="Quantidade Mínima")
    fixed_price = fields.Float(string="Preço fixo")


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    value_price_ids = fields.Many2many(
        "product.attribute.value.price", relation="product_attribute_value_price_rel", string="Preço extra por quantidade")


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_product_price_extra(self):
        super(ProductProduct, self)._compute_product_price_extra()
        for product in self:
            quantity = self.env.context.get("quantity", 1)

            total_price = 0
            for value in product.product_template_attribute_value_ids:
                prices = value.value_price_ids.filtered(lambda x: x.min_quantity < quantity).sorted("min_quantity")
                total_price += (prices and prices[0].fixed_price or 0) / quantity

            product.price_extra = product.price_extra + total_price
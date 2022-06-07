

from odoo import api, fields, models


class ProductAttributeValuePrice(models.Model):
    _name = 'product.attribute.value.price'
    _description = 'Cria uma tabela de preco quantidade por atributo'
    _order = "min_quantity"

    min_quantity = fields.Float(string="Quantidade Mínima")
    fixed_price = fields.Float(string="Preço")
    price_type = fields.Selection([
        ("unit", "Unitário"), ("thousand", "Milheiro"), ("fixed", "Fixo")],
        default="unit", string="Tipo de Preço")


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    value_price_ids = fields.Many2many(
        "product.attribute.value.price", string="Preço extra por quantidade")


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_product_price_extra(self):
        super(ProductProduct, self)._compute_product_price_extra()
        for product in self:
            quantity = self.env.context.get("quantity", 1)

            total_price = 0
            for prd_value in product.product_template_attribute_value_ids:

                attr_value = prd_value.product_attribute_value_id
                prices = attr_value.value_price_ids.filtered(lambda x: x.min_quantity < quantity).sorted("min_quantity", reverse=True)
                if prices:
                    price_type = prices[0].price_type

                    if price_type == "unit":
                        total_price += prices[0].fixed_price
                    elif price_type == "thousand":
                        multiplier = quantity // 1000
                        remainder = quantity % 1000

                        total_price += (prices[0].fixed_price / quantity) * multiplier
                        if remainder:
                            total_price += prices[0].fixed_price / remainder

                    elif price_type == "fixed":
                        total_price += prices[0].fixed_price / quantity

            product.price_extra = product.price_extra + total_price

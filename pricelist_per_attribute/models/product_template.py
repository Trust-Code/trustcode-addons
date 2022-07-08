

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

    multiply_attribute_cost = fields.Boolean(string="Multiplicar o custo de gravacao?")
    cost_multiplier = fields.Integer(string="Multiplicador")

    value_price_ids = fields.Many2many(
        "product.attribute.value.price", string="Preço extra por quantidade")


class ProductProduct(models.Model):
    _inherit = "product.product"

    def price_compute(self, price_type, uom=False, currency=False, company=None):
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['uom.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        products = self
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            products = self.with_company(company or self.env.company).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:
            prices[product.id] = product[price_type] or 0.0
            if price_type in ('list_price', 'standard_price'):
                print(product.price_extra)
                prices[product.id] += product.price_extra
                # we need to add the price from the attributes that do not generate variants
                # (see field product.attribute create_variant)
                if self._context.get('no_variant_attributes_price_extra'):
                    # we have a list of price_extra that comes from the attribute values, we need to sum all that
                    prices[product.id] += sum(self._context.get('no_variant_attributes_price_extra'))

            if uom:
                prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[product.id] = product.currency_id._convert(
                    prices[product.id], currency, product.company_id, fields.Date.today())

        return prices

    def _compute_product_price_extra(self):
        super(ProductProduct, self)._compute_product_price_extra()
        for product in self:
            quantity = self.env.context.get("quantity", 1)

            total_price = 0
            multiplier = product.product_template_attribute_value_ids.filtered(lambda x: x.product_attribute_value_id.multiply_attribute_cost)
            for prd_value in product.product_template_attribute_value_ids:

                attr_value = prd_value.product_attribute_value_id
                prices = attr_value.value_price_ids.filtered(lambda x: x.min_quantity <= quantity).sorted("min_quantity", reverse=True)
                if prices:
                    price_type = prices[0].price_type

                    if price_type == "unit":
                        total_price += prices[0].fixed_price
                    elif price_type == "thousand":
                        multiple = quantity // 1000
                        remainder = quantity % 1000

                        total_price += (prices[0].fixed_price / quantity) * multiple
                        if remainder:
                            total_price += prices[0].fixed_price / remainder

                    elif price_type == "fixed":
                        total_price += prices[0].fixed_price / quantity

            if multiplier:
                total_price = total_price * multiplier.product_attribute_value_id.cost_multiplier

            product.price_extra = product.price_extra + total_price

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def call_wizard_sale_variant(self):
        return ['action'] = self.env.ref('sale_variant_configurator.action_sale_variant_wizard')

from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def update_taxes(self):
        if self.fiscal_position_id:
            for line in self.invoice_line_ids:
                price_unit = line.price_unit
                line._onchange_product_id()
                line._br_account_onchange_product_id()
                line.write({'price_unit': price_unit})

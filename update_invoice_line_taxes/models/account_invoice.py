from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def update_taxes(self):
        if self.fiscal_position_id:
            for line in self.invoice_line_ids:
                price_unit = line.price_unit
                line._onchange_product_id()
                line._br_account_onchange_product_id()

                line.icms_aliquota = line.tax_icms_id.amount
                line.icms_st_aliquota = line.tax_icms_st_id.amount
                line.pis_aliquota = line.tax_pis_id.amount
                line.cofins_aliquota = line.tax_cofins_id.amount
                line.ipi_aliquota = line.tax_ipi_id.amount
                line.ii_aliquota = line.tax_ii_id.amount
                line.issqn_aliquota = line.tax_issqn_id.amount
                line.csll_aliquota = line.tax_csll_id.amount
                line.irrf_aliquota = line.tax_irrf_id.amount
                line.inss_aliquota = line.tax_inss_id.amount

                line.write({'price_unit': price_unit})

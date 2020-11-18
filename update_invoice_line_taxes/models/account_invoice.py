from odoo import models

TAXES = ['icms', 'icms_st', 'icms_fcp', 'icms_inter',
         'icms_intra', 'ipi', 'pis', 'cofins',
         'issqn', 'ii', 'irrf', 'csll', 'inss']


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def update_taxes(self):
        fpos = self.fiscal_position_id
        if fpos and self.state == 'draft':
            with self.env.norecompute():
                for line in self.invoice_line_ids:
                    price_unit = line.price_unit
                    if price_unit == 0.0:
                        continue
                    account_analytic_id = line.account_analytic_id.id
                    self.clear_line_tax_ids(line)
                    line._set_taxes_from_fiscal_pos()
                    line._set_taxes()
                    line._onchange_product_id()
                    line._br_account_onchange_product_id()
                    line._set_extimated_taxes(line.price_unit)
                    self._set_all_taxes_amount(line)
                    line.write({
                        'price_unit': price_unit,
                        'account_analytic_id': account_analytic_id
                    })
                self._onchange_invoice_line_ids()
            self.recompute()

    def _set_all_taxes_amount(self, line):
        for tax in TAXES:
            str_onchange = '_onchange_tax_%s_id' % tax
            onchange = getattr(line, str_onchange)
            if onchange:
                onchange()

    def clear_line_tax_ids(self, line):
        line.tem_difal = False

        vals = {}
        for tax in TAXES:
            vals['tax_%s_id' % tax] = False
            if tax not in ('icms_st', 'icms_fcp', 'icms_inter', 'icms_intra'):
                vals['%s_rule_id' % tax] = False

        line.update(vals)

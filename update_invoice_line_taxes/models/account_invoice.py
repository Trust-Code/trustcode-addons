from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def update_taxes(self):
        fpos = self.fiscal_position_id
        if fpos:
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
                line.write({
                    'price_unit': price_unit,
                    'account_analytic_id': account_analytic_id
                })
            self._onchange_invoice_line_ids()

    def clear_line_tax_ids(self, line):
        line.tem_difal = False
        taxes = ['icms', 'ipi', 'pis', 'cofins',
                 'issqn', 'ii', 'irrf', 'csll', 'inss']
        for tax in taxes:
            line.update({
                ('tax_%s_id' % tax): False,
                ('%s_rule_id' % tax): False})
        line.update({'tax_icms_st_id': False})

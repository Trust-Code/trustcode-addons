from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def update_taxes(self):
        fpos = self.fiscal_position_id
        if fpos:
            for line in self.invoice_line_ids:
                self.clear_line_tax_ids(line)
                line._set_taxes_from_fiscal_pos()
                unused_fields = fpos.map_tax_extra_values_unused(
                    self.company_id, line.product_id, self.partner_id)
                for field in unused_fields:
                    if field in line._fields:
                        line.update({field: False})

    def clear_line_tax_ids(self, line):
        line.tem_difal = False
        taxes = [
            'tax_pis_id', 'tax_icms_id', 'tax_icms_st_id', 'tax_ipi_id',
            'tax_cofins_id', 'tax_issqn_id', 'tax_ii_id', 'tax_csll_id',
            'tax_irrf_id', 'tax_inss_id']
        for tax in taxes:
            line.update({tax: False})


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    @api.model
    def map_tax_extra_values_unused(self, company, product, partner):
        to_state = partner.state_id

        taxes = ('icms', 'simples', 'ipi', 'pis', 'cofins',
                 'issqn', 'ii', 'irrf', 'csll', 'inss')
        res = []
        for tax in taxes:
            vals = self._filter_rules(
                self.id, tax, partner, product, to_state)
            for k, v in vals.items():
                if not v:
                    res.append(k)
        return res

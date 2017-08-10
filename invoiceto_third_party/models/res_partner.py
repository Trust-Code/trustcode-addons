# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoiceto_id = fields.Many2one('res.partner', string=u"Faturar para")

    @api.multi
    def address_get(self, adr_pref=None):
        res = super(ResPartner, self).address_get(adr_pref=adr_pref)
        if self.invoiceto_id:
            res['invoice'] = self.invoiceto_id.id
        return res

    def open_partner_history(self):
        res = super(ResPartner, self).open_partner_history()
        res['domain'] = ['!', ('partner_id', 'in', self.ids),
                         ('partner_shipping_id', 'in', self.ids)]
        return res

    @api.multi
    def _invoice_total(self):
        super(ResPartner, self)._invoice_total()
        for partner in self:
            if partner.invoiceto_id:
                account_invoice_report = self.env['account.invoice.report']

                # generate where clause to include multicompany rules
                where = account_invoice_report._where_calc([
                    ('partner_id', '=', partner.invoiceto_id.id),
                    ('state', 'not in', ['draft', 'cancel']),
                    ('company_id', '=', self.env.user.company_id.id),
                    ('type', 'in', ('out_invoice', 'out_refund'))
                ])
                account_invoice_report._apply_ir_rules(where, 'read')
                from_clause, where_clause, where_params = where.get_sql()

                # price_total is in the company currency
                query = """
                          SELECT SUM(price_total) as total, partner_id
                            FROM account_invoice_report account_invoice_report
                           WHERE %s
                           GROUP BY partner_id
                        """ % where_clause
                self.env.cr.execute(query, where_params)
                price_totals = self.env.cr.dictfetchall()
                partner.total_invoiced += sum(
                    price['total'] for price in price_totals)

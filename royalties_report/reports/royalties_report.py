# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class RoyaltiesReport(models.AbstractModel):
    _name = 'report.royalties_report.royalties_report'

    @api.model
    def render_html(self, docids, data=None):
        import ipdb
        ipdb.set_trace()
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'royalties_report.royalties_report')
        account_voucher = self.env['account.voucher'].search(
                            [('id', 'in', docids)])
        royalties_lines = self.env['account.royalties.line'].search(
                            [('voucher_id', '=', account_voucher.id)])

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': account_voucher,
            'royalties_lines': royalties_lines,
        }
        return report_obj.render(
            'royalties_report.royalties_report', docargs)

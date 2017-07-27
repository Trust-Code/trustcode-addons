# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
import datetime


class RoyaltiesReport(models.AbstractModel):
    _name = 'report.royalties_report.royalties_report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'royalties_report.royalties_report')
        account_voucher = self.env['account.voucher'].search(
            [('id', 'in', docids)])
        royalties_lines = self.env['account.royalties.line'].search(
            [('voucher_id', '=', account_voucher.id)])

        period = self._get_period(royalties_lines[0].royalties_id,
                                  account_voucher)

        initial_date = datetime.datetime.strptime(
            period['initial_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        final_date = datetime.datetime.strptime(
            period['final_date'], '%Y-%m-%d').strftime('%d/%m/%Y')

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': account_voucher,
            'royalties_lines': royalties_lines,
            'initial_date': initial_date,
            'final_date': final_date
        }
        return report_obj.render(
            'royalties_report.royalties_report', docargs)

    def _get_period(self, royalties_id, voucher_id):
        account_voucher = self.env['account.voucher'].search(
            [('royalties_id', '=', royalties_id.id),
             ('id', '<', voucher_id.id)], order='id desc', limit=1)

        if not account_voucher:
            return {'initial_date': royalties_id.start_date,
                    'final_date': voucher_id.account_date}
        else:
            return {'initial_date': account_voucher.account_date,
                    'final_date': voucher_id.account_date}

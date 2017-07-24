# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class RoyaltiesReport(models.AbstractModel):
    _name = 'report.royalties_report.report_royalties_main'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'royalties_report.template_royalties_report_main')
        royalties = self.env['royalties'].search([('id', 'in', docids)])

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': royalties,
        }
        return report_obj.render(
            'royalties_report.template_royalties_report_main', docargs)

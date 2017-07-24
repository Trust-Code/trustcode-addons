# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class RoyaltiesReport(models.AbstractModel):
    _name = 'report.royalties_report.royalties_report_main'

    @api.model
    def render_html(self, docids, data=None):
        import ipdb
        ipdb.set_trace()
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'royalties_report.main_template_royalties_report')
        royalties = self.env['royalties'].search([('id', 'in', docids)])

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': royalties,
        }
        return report_obj.render(
            'royalties_report.main_template_royalties_report', docargs)

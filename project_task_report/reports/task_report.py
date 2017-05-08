# -*- encoding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProjectTaskReport(models.AbstractModel):
    _name = 'report.project_task_report.report_project_task_main'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'project_task_report.report_project_task_main')
        hour_count = 0
        tasks = self.env['project.task'].search([('id', 'in', docids)])
        for task in tasks:
            hour_count += task.effective_hours

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': tasks,
            'hours': hour_count
        }
        return report_obj.render(
            'project_task_report.report_project_task_main', docargs)

# -*- coding: utf-8 -*-
# © 2015 Mackilem Van der Lan, Trustcode
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, tools
from datetime import datetime


class ProjectTask (models.Model):
    _inherit = 'project.task'

    _order = "priority desc, date_deadline, sequence, date_start, name, id"

    def start_track_time(self, stage_name, user_id):
        df = tools.DEFAULT_SERVER_DATETIME_FORMAT
        self.env['account.analytic.line'].sudo().create(
            {'name': u'Tempo Automático (%s)' % (stage_name),
             'task_id': self.id,
             'project_id': self.project_id.id,
             'date': datetime.now().strftime(df),
             'start_date': datetime.now().strftime(df),
             'user_id': user_id,
             'partner_id': self.partner_id.id,
             'unit_amount': 0.0,
             'running_time': True})
        return

    def stop_track_time(self, user_id):
        task_work = self.env['account.analytic.line'].sudo().search(
            [('user_id', '=', user_id),
             ('running_time', '=', True),
             ('task_id', '=', self.id)],
            order='id desc', limit=1)

        if task_work:
            ff = tools.DEFAULT_SERVER_DATETIME_FORMAT
            count_time = datetime.now() - datetime.strptime(
                task_work.start_date, ff)

            task_work.write({
                'unit_amount': count_time.total_seconds() / 60.0 / 60.0,
                'running_time': False,
                'end_date': datetime.now()
            })
        return

    @api.multi
    def write(self, vals):
        if "stage_id" in vals:
            next_stage = self.env['project.task.type'].browse(vals["stage_id"])
            if next_stage.tracking_time:
                self.start_track_time(
                    next_stage.name, self.user_id.id or self.env.user.id)
            else:
                self.stop_track_time(self.user_id.id or self.env.user.id)

        elif "kanban_state" in vals:
            if vals["kanban_state"] == "normal":
                self.start_track_time(
                    self.stage_id.name, self.user_id.id or self.env.user.id)
            else:
                self.stop_track_time(self.user_id.id or self.env.user.id)

        elif "user_id" in vals and self.stage_id.tracking_time:
            self.stop_track_time(self.user_id.id or self.env.user.id)
            self.start_track_time(
                self.stage_id.name, vals["user_id"] or self.env.user.id)

        return super(ProjectTask, self).write(vals)


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    tracking_time = fields.Boolean(u'Registrar Tempo neste estágio?')


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    start_date = fields.Datetime(u'Inicio Atividade')
    end_date = fields.Datetime(u'Fim Atividade')
    running_time = fields.Boolean(u'Em execução')


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def attendance_action_change(self):
        res = super(HrEmployee, self).attendance_action_change()
        if self.attendance_state == 'checked_out':
            tasks = self.env['project.task'].search(
                [('user_id', '=', self.user_id.id),
                 ('stage_id.tracking_time', '=', True),
                 ('kanban_state', '=', 'normal')])
            for task in tasks:
                task.write({'kanban_state': 'blocked'})
        return res

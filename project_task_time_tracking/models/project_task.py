# -*- coding: utf-8 -*-
# © 2015 Mackilem Van der Lan, Trustcode
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from datetime import datetime


class ProjectTask (models.Model):
    _inherit = 'project.task'

    _order = "priority desc, date_deadline, sequence, date_start, name, id"

    def start_track_time(self, stage_name, user_id):
        self.env['account.analytic.line'].sudo().create(
            {'name': u'Tempo Automático (%s)' % (stage_name),
             'task_id': self.id,
             'project_id': self.project_id.id,
             'date': datetime.now(),
             'start_date': datetime.now(),
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
            count_time = datetime.now() - task_work.start_date

            task_work.write({
                'unit_amount': count_time.total_seconds() / 60.0 / 60.0,
                'running_time': False,
                'end_date': datetime.now()
            })
        return

    def to_hours(self, val):
        hour = int(val)
        minutes = int(60 * (val - hour))
        return '{}:{}'.format(str(hour).zfill(2), str(minutes).zfill(2))

    def insert_new_line(self, name, before, after=False):
        message = '<li>{}: {}'.format(name, before)
        if after:
            message += '  -->  {}'.format(after)
        message += '</li>'
        return message

    def message_post_timesheet_create(self, vals):
        message = 'Registro de horas criado por {}:'.format(
            self.env.user.partner_id.name)
        message += '<ul>'
        message += self.insert_new_line('Data', vals['date'])
        employee = self.env['hr.employee'].browse(vals['employee_id']).name
        message += self.insert_new_line('Funcionário', employee)
        message += self.insert_new_line('Descrição', vals['name'])
        message += self.insert_new_line('Duração', self.to_hours(
            vals['unit_amount']))
        message += '</ul>'
        self.message_post(body=message)

    def message_post_timesheet_change(self, changes):
        for change in changes:
            if not (change[2]):
                continue
            if not change[0]:
                self.message_post_timesheet_create(change[2])
                continue
            timesheet = self.env['account.analytic.line'].browse(change[1])
            message = 'Registro de horas alterado por {}:'.format(
                self.env.user.partner_id.name)
            message += '<ul>'
            after = False
            if change[2].get('date'):
                after = change[2]['date']
            message += self.insert_new_line(
                'Data', timesheet.date.strftime('%d-%m-%Y'), after)
            employee = False
            if change[2].get('employee_id'):
                employee = self.env['hr.employee'].browse(
                    change[2]['employee_id']).name
            message += self.insert_new_line(
                'Funcionário',
                timesheet.employee_id.name, employee)
            unit_before = self.to_hours(timesheet.unit_amount)
            unit = False
            if change[2].get('unit_amount'):
                unit = self.to_hours(change[2]['unit_amount'])
            message += self.insert_new_line('Duração', unit_before, unit)
            after = False
            if change[2].get('name'):
                after = change[2]['name']
            message += self.insert_new_line('Descrição', timesheet.name, after)
            message += '</ul>'
            self.message_post(body=message)

    @api.multi
    def write(self, vals):
        if "stage_id" in vals:
            next_stage = self.env['project.task.type'].browse(vals["stage_id"])
            if next_stage.tracking_time:
                self.start_track_time(
                    next_stage.name, self.user_id.id or self.env.user.id)
            else:
                self.stop_track_time(self.user_id.id or self.env.user.id)

        elif "kanban_state" in vals and self.stage_id.tracking_time:
            if vals["kanban_state"] == "normal":
                self.start_track_time(
                    self.stage_id.name, self.user_id.id or self.env.user.id)
            else:
                self.stop_track_time(self.user_id.id or self.env.user.id)

        elif "user_id" in vals and self.stage_id.tracking_time:
            self.stop_track_time(self.user_id.id or self.env.user.id)
            self.start_track_time(
                self.stage_id.name, vals["user_id"] or self.env.user.id)
        if vals.get('timesheet_ids'):
            self.message_post_timesheet_change(vals['timesheet_ids'])
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

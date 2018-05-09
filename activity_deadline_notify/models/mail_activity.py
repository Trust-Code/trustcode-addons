# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTFT
from odoo.exceptions import UserError


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    datetime_deadline = fields.Datetime('Data de Vencimento')
    enable_notification = fields.Boolean('Notificação')
    notification_time = fields.Integer('Lembrete')
    notification_interval = fields.Selection(
        [('minutes', 'Minutos'),
         ('hours', 'Horas'),
         ('days', 'Dias')], 'Intervalo', default="minutes")

    def to_seconds(self, value, time):
        time_table = {
            'minutes': 60,
            'hours': 60*60,
            'days': 24*60*60,
        }
        return value * time_table[time]

    def get_notification_time(self, time_now, time, interval):
        if time:
            secs = self.to_seconds(time, interval)
            time_now -= timedelta(seconds=secs)
        return time_now

    def update_date_deadline(self, vals):
        datetime_value = datetime.strptime(vals['datetime_deadline'], DTFT)
        if datetime_value < datetime.now():
            raise UserError('O tempo de vencimento é menor que o tempo\
                atual.')
        vals.update({'date_deadline': datetime.strftime(
            datetime_value.date(), DTFT)})
        return vals

    def create_notification(self, vals):
        datetime_value = datetime.strptime(vals['datetime_deadline'], DTFT)
        if vals['enable_notification']:
            notification_time = self.get_notification_time(
                datetime_value,
                vals['notification_time'],
                vals['notification_interval'])
            self.env['mail.activity.notify'].create({
                'activity_id': self.id,
                'notification_time': datetime.strftime(
                    notification_time, DTFT),
            })

    @api.model
    def create(self, vals):
        if vals.get('datetime_deadline'):
            vals = self.update_date_deadline(vals)
        res = super(MailActivity, self).create(vals)
        res.create_notification(vals)
        return res

    @api.multi
    def update_notify_time(self):
        for activity in self:
            datetime_val = datetime.strptime(activity.datetime_deadline, DTFT)
            notif_time = self.get_notification_time(
                datetime_val, activity.notification_time,
                activity.notification_interval)
            notif = self.env['mail.activity.notify'].search(
                [('activity_id', '=', activity.id)], limit=1)
            if notif:
                notif.notification_time = notif_time
            else:
                if activity.enable_notification:
                    self.env['mail.activity.notify'].create({
                        'activity_id': activity.id,
                        'notification_time': datetime.strftime(
                            notif_time, DTFT)
                    })

    @api.multi
    def write(self, vals):
        if vals.get('datetime_deadline'):
            vals = self.update_date_deadline(vals)
        res = super(MailActivity, self).write(vals)
        self.update_notify_time()
        return res


class MailActivityNotification(models.Model):
    _name = 'mail.activity.notify'

    activity_id = fields.Many2one('mail.activity', 'Atividade', required=True)
    notification_time = fields.Datetime('Hora da notificação')

    def cron_check_notifications(self):
        notifications = self.env['mail.activity.notify'].search([
            ]).filtered(lambda x: datetime.strptime(x.notification_time, DTFT)
                        <= datetime.now())
        for notification in notifications:
            act = notification.activity_id
            title = 'Atividade: ' + (act.res_name or '')
            message = (act.activity_type_id.name or '') + ': ' +\
                (act.summary or '')
            redirect = {
                'name': 'Atividades',
                'model': act.res_model,
                'view': 'kanban',
                'domain': [['id', '=', act.res_id]],
                'context': {}
            }
            act.user_id.notify(message, title, True, redirect)
            notification.unlink()

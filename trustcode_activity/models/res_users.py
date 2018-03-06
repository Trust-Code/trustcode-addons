# © 2018 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, modules


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def activity_user_count(self):
        query = """SELECT m.id, count(*), act.res_model as model,
                        CASE
                            WHEN now() at time zone 'utc' - act.date_deadline between '-1 min'::interval and '1 min'::interval Then 'today'
                            WHEN now() at time zone 'utc' - act.date_deadline > '1 min'::interval Then 'overdue'
                            WHEN now() at time zone 'utc' - act.date_deadline < '1 min'::interval Then 'planned'
                        END AS states
                    FROM mail_activity AS act
                    JOIN ir_model AS m ON act.res_model_id = m.id
                    WHERE user_id = %s
                    GROUP BY m.id, states, act.res_model;
                    """
        self.env.cr.execute(query, [self.env.uid])
        activity_data = self.env.cr.dictfetchall()
        model_ids = [a['id'] for a in activity_data]
        model_names = {n[0]:n[1] for n in self.env['ir.model'].browse(model_ids).name_get()}

        user_activities = {}
        for activity in activity_data:
            if not user_activities.get(activity['model']):
                user_activities[activity['model']] = {
                    'name': model_names[activity['id']],
                    'model': activity['model'],
                    'icon': modules.module.get_module_icon(self.env[activity['model']]._original_module),
                    'total_count': 0, 'today_count': 0, 'overdue_count': 0, 'planned_count': 0,
                }
            user_activities[activity['model']]['%s_count' % activity['states']] += activity['count']
            if activity['states'] in ('today','overdue'):
                user_activities[activity['model']]['total_count'] += activity['count']

        return list(user_activities.values())

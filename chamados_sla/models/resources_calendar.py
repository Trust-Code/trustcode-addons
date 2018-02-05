# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    @api.multi
    def plan_hours(self, hours, day_dt, compute_leaves=False,
                   resource_id=None):
        """ Return datetime after having planned hours """
        res = self._schedule_hours(hours, day_dt, compute_leaves, resource_id)
        if res and hours < 0.0:
            return res[0][0]
        elif res:
            return res[-1][1]
        return False

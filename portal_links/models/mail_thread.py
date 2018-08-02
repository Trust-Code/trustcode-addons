# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models

class PortalLinks(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def _notification_link_helper(self, link_type, **kwargs):
        res = super(PortalLinks, self)._notification_link_helper('view')

        if self._name == 'project.task':
            link = "/my/task/%s?" % (self.id)

        return link

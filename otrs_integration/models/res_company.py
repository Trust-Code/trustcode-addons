# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    otrs_domain = fields.Char('OTRS Domain')
    otrs_webservice_name = fields.Char('OTRS WebService')

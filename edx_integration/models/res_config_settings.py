# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna <fabiocluna@hotmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    edx_url = fields.Char('Url base para acesso ao EDX')
    edx_client_id = fields.Char('EDX client id')
    edx_client_secret = fields.Char('EDX client secret')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            edx_url=str(params.get_param(
                'edx_integration.edx_url', default="")) or "",
            edx_client_id=str(params.get_param(
                'edx_integration.edx_client_id', default="")) or "",
            edx_client_secret=str(params.get_param(
                'edx_integration.edx_client_secret', default="")) or ""
        )

        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'edx_integration.edx_url', self.edx_url)
        self.env['ir.config_parameter'].sudo().set_param(
            'edx_integration.edx_client_id', self.edx_client_id)
        self.env['ir.config_parameter'].sudo().set_param(
            'edx_integration.edx_client_secret', self.edx_client_secret)

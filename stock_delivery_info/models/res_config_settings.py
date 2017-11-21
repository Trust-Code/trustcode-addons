# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    endpoint_stock_delivery = fields.Char('Endpoint Stock Delivery')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res['endpoint_stock_delivery'] = params.get_param(
            'stock.endpoint_stock_delivery', default='')

        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param(
            "stock.endpoint_stock_delivery",
            (self.endpoint_stock_delivery or "").strip())

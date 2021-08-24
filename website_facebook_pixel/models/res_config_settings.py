# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    facebook_pixel_key = fields.Char(
        related='website_id.facebook_pixel_key',
        readonly=False,
    )

    @api.depends('website_id')
    def has_facebook_pixel(self):
        self.has_facebook_pixel = bool(self.facebook_pixel_key)

    def inverse_has_facebook_pixel(self):
        if not self.has_facebook_pixel:
            self.facebook_pixel_key = False

    has_facebook_pixel = fields.Boolean(
        string='Facebook Pixel',
        compute=has_facebook_pixel,
        inverse=inverse_has_facebook_pixel,
    )

# -*- coding: utf-8 -*-

from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    facebook_pixel_key = fields.Char('Facebook Pixel ID')

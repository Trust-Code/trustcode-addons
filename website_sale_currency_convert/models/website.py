
from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    def _compute_usd_price(self):
        usd_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        for item in self:
            item.usd_currency_id = usd_id.id

    usd_currency_id = fields.Many2one('res.currency', compute="_compute_usd_price")

from datetime import date
from odoo import models, fields


class MonetaryAdjustmentRatio(models.Model):
    _name = "monetary.adjustment.ratio"

    current_ratio = fields.Float(
        'Current Adjustment Ratio', compute='_compute_current_ratio')
    name = fields.Char('Name')

    def _compute_current_ratio(self):
        for item in self:
            ratio = self.env['monetary.adjustment.rate'].search(
                [('name', '<=', date.today()),
                 ('ratio_id', '=', item.id)], limit=1, order='name desc')
            if ratio:
                item.current_ratio = ratio.rate
            else:
                item.current_ratio = 0.0


class MonetaryAdjustmentRate(models.Model):
    _name = "monetary.adjustment.rate"
    _order = 'name desc'

    rate = fields.Float('Adjustment Rate')
    name = fields.Date('Data')
    ratio_id = fields.Many2one('monetary.adjustment.ratio')

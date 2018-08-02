from odoo import models, fields


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    next_adjustment = fields.Date('Next Adjustment')
    monetary_ratio = fields.Many2one(
        'monetary.adjustment.ratio', 'Monetary Ratio')
    due_date_behavior = fields.Selection([
        ('anticipate', 'Anticipate'),
        ('maintain', 'Maintain'),
        ('postpone', 'Postpone')], string="Due Date Behavior")

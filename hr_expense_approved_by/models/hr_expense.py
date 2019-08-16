
from odoo import fields, models


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    responsible_id = fields.Many2one(
        'res.users', related='sheet_id.responsible_id', readonly=True)

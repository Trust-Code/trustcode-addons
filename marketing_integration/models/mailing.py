
from odoo import fields, models


class MassMailing(models.Model):
    _inherit = 'mailing.mailing'
    
    mailing_model_id = fields.Many2one(domain=[])

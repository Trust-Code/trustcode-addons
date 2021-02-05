from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    use_boleto_cloud = fields.Boolean('Usar Boleto Cloud')



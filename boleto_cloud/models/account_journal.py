from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    use_boleto_cloud = fields.Boolean('Usar Boleto Cloud')
    boleto_cloud_bank_account_api_key = fields.Char('Chave API da Conta')
    instrucoes = fields.Char('Instruções do Boleto')



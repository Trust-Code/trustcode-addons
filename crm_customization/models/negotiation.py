from odoo import models, fields, api


class NegotiationRule(models.Model):
    _name = 'negotiation.rule'
    _order = 'vencido_ate_dias'
    
    vencido_ate_dias = fields.Integer(string="Vencido até (dias)")
    percentual_multa = fields.Float(string="% de multa")
    percentual_juros_mora = fields.Float(string="% de juros (mora)")

   # Criação de regra de negócio com valores de parcelas e juros pré determinadas com base no 
   # quantidade de dias que o título esta vencido x valor da Oportunidade
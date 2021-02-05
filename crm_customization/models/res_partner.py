from odoo import api, fields, models
from datetime import datetime

class ResPartner(models.Model):
    _inherit ='res.partner'

    # Vai servir para coligada e filial
    codigo_parceiro = fields.Char(string="Código")

    registro_aluno = fields.Char(size=30, string="Registro do Aluno")
    data_nascimento = fields.Date(string="Data de Nascimento")
    estado_civil = fields.Selection(
        [('solteiro', 'Solteiro'), ('casado', 'Casado'), 
         ('separado', 'Separado'), ('viuvo', 'Viúvo')])
    sexo = fields.Selection([('masculino', 'Masculino'), ('feminino', 'Feminino')])

    coligada_id = fields.Many2one('res.partner', string='Coligada')
    cfo_partner_id = fields.Many2one('res.partner', string='CFO')
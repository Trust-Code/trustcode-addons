from odoo import api, fields, models
from datetime import datetime

class ResPartner(models.Model):
    _inherit ='res.partner'
   
    codigo_coligada = fields.Char(size=30, string="Código Coligada")
    codigo_cfo = fields.Char(size=30, string="Código CFO")
    registro_aluno = fields.Char(size=30, string="Registro do Aluno")
    data_nascimento = fields.Date(string="Data de Nascimento")
    estado_civil = fields.Selection(
        [('solteiro', 'Solteiro'), ('casado', 'Casado'), 
         ('separado', 'Separado'), ('viuvo', 'Viúvo')])
    sexo = fields.Selection([('masculino', 'Masculino'), ('feminino', 'Feminino')])

    
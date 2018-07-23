from odoo import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    ref = fields.Char('Ref')
    color_code = fields.Char('Código Cor')
    size = fields.Char('Tamanho')
    trat = fields.Char('Trat')
    left_angle = fields.Char('Angulo Esquerdo')
    right_angle = fields.Char('Angulo Direito')
    height = fields.Float('Altura')
    width = fields.Float('Largura')
    surface = fields.Char('Superficie')

    is_component = fields.Boolean(default=False)
    is_profile = fields.Boolean(default=False)
    is_glass = fields.Boolean(default=False)

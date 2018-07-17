# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    projetista = fields.Char('Projetista')
    height = fields.Float('Altura')
    width = fields.Float('Largura')
    # o que eh TRAT_PERF
    trat_perf = fields.Char('Trat_Perf')


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    ref = fields.Char('Ref')
    color_code = fields.Char('Código Cor')
    size = fields.Char('Tamanho')
    # o que eh TRAT?
    trat = fields.Char('Trat')
    left_angle = fields.Char('Angulo Esquerdo')
    right_angle = fields.Char('Angulo Direito')
    height = fields.Float('Altura')
    width = fields.Float('Largura')
    surface = fields.Char('Superficie')

    is_component = fields.Boolean(default=False)
    is_profile = fields.Boolean(default=False)
    is_glass = fields.Boolean(default=False)

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    projetista = fields.Char('Projetista')
    height = fields.Float('Altura')
    width = fields.Float('Largura')
    trat_perf = fields.Char('Trat_Perf')

    def _generate_raw_move(self, bom_line, line_data):
        res = super(MrpProduction, self)._generate_raw_move(
            bom_line, line_data)
        # update or write?
        res.write({
            'ref': bom_line.ref or '',
            'color_code': bom_line.color_code or '',
            'size': bom_line.size or '',
            'trat': bom_line.trat or '',
            'left_angle': bom_line.left_angle or '',
            'right_angle': bom_line.right_angle or '',
            'height': bom_line.height or 0.0,
            'width': bom_line.width or 0.0,
            'surface': bom_line.surface or '',
            'is_component': bom_line.is_component or False,
            'is_profile': bom_line.is_profile or False,
            'is_glass': bom_line.is_glass or False,
        })
        return res

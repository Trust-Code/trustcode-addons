from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    bom_dynamic_line_ids = fields.Many2many('bom.dynamic.line')

    def retorna_lista_codigos(self, cod_atributos):

        # Dentro do safe_eval, é selecionado os códigos de produtos
        codigos = []
        for item in self.bom_dynamic_line_ids:
            # Recebe uma lista de códigos de atributos
            eval_context = {"ATR": cod_atributos}

            safe_eval(item.codigo.strip(),
                      eval_context, mode="exec", nocopy=True)
            if 'result' in eval_context and eval_context['result']:
                codigos.append(eval_context['result'])
        return codigos


class BomDynamicLine(models.Model):
    _name = "bom.dynamic.line"
    _order = "id"

    bom_id = fields.Many2one(
        'mrp.bom', 'Parent BoM',
        index=True, ondelete='cascade',
        required=True)

    name = fields.Char(string="Nome")

    codigo = fields.Text(string="Código")

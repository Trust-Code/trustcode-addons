from odoo import models, fields, api


class ProjectArt(models.Model):
    _inherit = 'project.project'

    kk_site_code = fields.Char('Código KK', related='kk_site_id.cod_site_kk', store=True)
    id_site_code = fields.Char('ID Site', related='kk_site_id.site_id', store=True)

    @api.depends('sale_line_id', 'sale_line_id.price_total')
    def _compute_art(self):
        if not self.sale_line_id or self.sale_line_id.price_total == 0:
            self.write({
                'art': 'N/E'
            })
        return

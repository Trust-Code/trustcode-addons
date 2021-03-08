from odoo import models, fields, api


class ProjectArt(models.Model):
    _inherit = 'project.project'

    kk_site_code = fields.Char('Código KK', related='kk_site_id.cod_site_kk', store=True)
    id_site_code = fields.Char('ID Site', related='kk_site_id.site_id', store=True)

    # teste
    project_self_id = fields.Many2one('project.project', compute='_compute_self_project_id', string='Projeto')

    @api.depends('sale_line_id', 'sale_line_id.price_total')
    def _compute_art(self):
        if not self.sale_line_id or self.sale_line_id.price_total == 0:
            self.write({
                'art': 'N/E'
            })
        return

    def _compute_self_project_id(self):
        for project in self:
            project.project_self_id = project

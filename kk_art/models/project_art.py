from odoo import models, fields


class ProjectArt(models.Model):
    _name = 'project.art'

    project_name = fields.Char('Nome do Projeto', required=True)
    partner_id = fields.Many2one('res.partner', 'Cliente')
    requester_id = fields.Many2one('res.users', 'Solicitante')
    kk_code = fields.Char('Código KK')
    site_id = fields.Char('ID Site')
    date_deadline = fields.Datetime('Data de Entrega')

    art = fields.Char('ART')


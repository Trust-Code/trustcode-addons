# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class Project(models.Model):
    _inherit = 'project.project'

    kk_site_id = fields.Many2one(
        'kk.sites',
        string="Site",
        store=True)
    art = fields.Char('ART')
    qualidade = fields.Char('Qualidade')
    data_entrega = fields.Date(
        'Data Previsão Entrega',
        compute='_compute_data_entrega')
    ultima_alteracao = fields.Datetime('Última Alteração')
    arquivado_fisicamente = fields.Date('Arquivado Fisicamente Em')
    obs = fields.Html('Observação')

    @api.multi
    def _compute_data_entrega(self):
        for project in self:
            data_entrega = project.task_ids.search(
                [('date_deadline', '!=', False),
                 ('project_id', '=', project.id)],
                order="date_deadline desc", limit=1).date_deadline
            if data_entrega:
                project.update({'data_entrega': data_entrega})


class Task(models.Model):
    _inherit = 'project.task'

    kk_site_id = fields.Many2one(
        'kk.sites',
        string="Site",
        store=True)

    @api.model
    def create(self, vals):
        project = self.env['project.project'].browse(vals['project_id'])
        if not vals.get('kk_site_id'):
            vals.update({'kk_site_id': project.kk_site_id.id})
        res = super(Task, self).create(vals)
        return res

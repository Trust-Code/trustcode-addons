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
    data_entrega = fields.Date('Data Previsão Entrega')
    ultima_alteracao = fields.Datetime('Última Alteração')
    arquivado_fisicamente = fields.Char('Arquivado Fisicamente Em')
    obs = fields.Html('Observação')


class Task(models.Model):
    _inherit = 'project.task'

    kk_site_id = fields.Many2one(
        'kk.sites',
        string="Site",
        store=True)

    @api.model
    def create(self, vals):
        res = super(Task, self).create(vals)
        res.kk_site_id = res.project_id.kk_site_id
        return res

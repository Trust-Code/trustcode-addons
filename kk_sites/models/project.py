# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
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
        'Data Previsão',
        compute='_compute_data_entrega')
    date_delivered = fields.Date('Data de Conclusão')
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
        if vals.get('stage_id'):
            res.update_date_delivered(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(Task, self).write(vals)
        if vals.get('stage_id'):
            self.update_date_delivered(vals)
        return res

    def update_date_delivered(self, vals):
        stages_done = self.env['project.task.type'].search(
            [('is_done', '=', True)])
        value = False
        if all(tasks.stage_id.id in stages_done.ids for tasks in
               self.project_id.task_ids):
            value = datetime.datetime.now()
        self.project_id.date_delivered = value


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_done = fields.Boolean('Concluído')

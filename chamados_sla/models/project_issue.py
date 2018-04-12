# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError
import re

ALTA = '2'
MEDIA = '1'
BAIXA = '0'

PRIORITY_TABLE = {
    ALTA: {
        ALTA: (0.25, 4),
        MEDIA: (0.25, 4),
        BAIXA: (0.25, 8)
        },
    MEDIA: {
        ALTA: (0.25, 4),
        MEDIA: (0.25, 8),
        BAIXA: (1, 24)
        },
    BAIXA: {
        ALTA: (0.25, 8),
        MEDIA: (1, 24),
        BAIXA: (2, 36)
        }
    }


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    tempo_resposta = fields.Datetime(string=u"Prazo 1º Atend.",
                                     store=True,
                                     compute="_compute_tempo")
    tempo_resolucao = fields.Datetime(string=u"Prazo Solução",
                                      store=True,
                                      compute="_compute_tempo")
    tempo_excedido = fields.Boolean(string="Tempo Excedido",
                                    store=True,
                                    compute="_compute_excedido")

    impacto = fields.Selection(
        [('0', 'Baixo'), ('1', 'Médio'), ('2', 'Alto')],
        string="Impacto sobre negócios", oldname='x_impacto',
        track_visibility='onchange')

    priority = fields.Selection(
        [('0', 'Low'), ('1', 'Normal'), ('2', 'High')],
        'Priority', index=True, default='0', track_visibility='onchange')

    @api.multi
    @api.depends("create_date", "priority", "impacto")
    def _compute_tempo(self):
        for item in self:
            if item.create_date and item.priority and item.impacto:
                valor = PRIORITY_TABLE[item.priority][item.impacto]
                data_python = fields.Datetime.from_string(item.create_date)
                calendar_id = item.project_id.resource_calendar_id
                item.tempo_resposta = calendar_id.plan_hours(
                    valor[0], data_python, compute_leaves=True)
                item.tempo_resolucao = calendar_id.plan_hours(
                    valor[1], data_python, compute_leaves=True)

    @api.multi
    def _compute_excedido(self):
        for item in self:
            result = False
            now = fields.Datetime.now()
            if item.stage_id.id not in [39, 40, 41, 62, 46, 47] \
               and now > item.tempo_resposta \
               and item.stage_id.sequence <= 10:
                result = True
            if item.stage_id.id not in [40, 41, 62, 46, 47] \
               and now > item.tempo_resolucao \
               and item.stage_id.sequence <= 100:
                result = True
            item.tempo_excedido = result

    def _check_description_characters(self, vals, onCreate=False):
        error = False
        if vals.get('description'):
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', vals['description'])
            desc_len = len(cleantext)
            if desc_len < 25:
                error = True
        elif onCreate:
            error = True
            desc_len = 0
        if error:
            raise UserError(u'A descrição contém apenas %d caracteres. Favor\
             descrever melhor o incidente. Este campo deve conter\
             no mínimo 25 caracteres' % desc_len)

    def _check_is_done(self, vals):
        if vals.get('stage_id'):
            if self.stage_id.block_stages_changes:
                raise UserError(u'Não é possível mudar o estágio de um chamado\
                    em %s' % self.stage_id.name)
            else:
                stage = self.env['project.task.type'].browse(vals['stage_id'])
                if stage.block_stages_changes:
                    self.is_issue_done = True

    @api.multi
    def write(self, vals):
        self._check_is_done(vals)
        self._check_description_characters(vals)
        return super(ProjectIssue, self).write(vals)

    @api.model
    def create(self, vals):
        self._check_description_characters(vals, True)
        return super(ProjectIssue, self).create(vals)

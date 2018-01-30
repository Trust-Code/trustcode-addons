# -*- encoding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError

# Estágio em que o issue será finalizado pelo cliente
STAGE_ID_CLOSED = 41


class ProjectIssue(models.Model):
    _inherit = "project.issue"

    can_close = fields.Boolean("Pode Fechar?")
    pergunta1 = fields.Selection([('sim', u'Sim'), ('nao', u'Não')])
    pergunta2 = fields.Selection([('otimo', u'Ótimo'), ('bom', u'Bom'),
                                  ('regular', u'Regular'), ('ruim', u'Ruim'),
                                  ('pessimo', u'Péssimo')])
    pergunta3 = fields.Selection([('otimo', u'Ótimo'), ('bom', u'Bom'),
                                  ('regular', u'Regular'), ('ruim', u'Ruim'),
                                  ('pessimo', u'Péssimo')])
    pergunta4 = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'),
                                  ('4', '4'), ('5', '5'), ('6', '6'),
                                  ('7', '7'), ('8', '8'), ('9', '9'),
                                  ('10', '10')])
    pergunta5 = fields.Text(string="Comentários")

    @api.multi
    def write(self, vals):
        res = super(ProjectIssue, self).write(vals)
        if "stage_id" in vals and vals['stage_id'] == STAGE_ID_CLOSED and \
           not self.can_close:
            raise UserError(u'Por favor, utilize o botão localizado dentro do \
            ticket para encerrar o chamado.')

        return res

    def action_close_issue(self):
        return self.env.ref(
            'issue_satisfaction_survey.action_issue_satifaction_survey'
        ).read()[0]

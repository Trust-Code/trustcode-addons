# -*- encoding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.exceptions import Warning

# Estágio em que o issue será finalizado pelo cliente
STAGE_ID_CLOSED = 41


class ProjectIssueClose(models.TransientModel):
    _name = "project.issue.close"

    pergunta1 = fields.Selection([('sim', u'Sim'), ('nao', u'Não')])
    pergunta2 = fields.Selection([('otimo', u'Ótimo'), ('bom', u'Bom'),
                                  ('regular', u'Regular'), ('ruim', u'Ruim'),
                                  ('pessimo', u'Péssimo')])
    pergunta3 = fields.Selection([('otimo', u'Ótimo'), ('bom', u'Bom'),
                                  ('regular', u'Regular'), ('ruim', u'Ruim'),
                                  ('pessimo', u'Péssimo')])

    pergunta4 = fields.Selection([('1', '1 - Muito Instatisfeito'),
                                  ('2', '2 - Insatisfeito'),
                                  ('3', '3 - Indiferente'),
                                  ('4', '4 - Satisfeito'),
                                  ('5', '5 - Muito Satisfeito')])

    def _validate_answer(self):
        result = True
        if not self.pergunta1 or not self.pergunta2 or not self.pergunta3 or \
           not self.pergunta4:
            result = False
            raise Warning('Você deverá preencher todas as perguntas antes de \
                           continuar')
        return result

    def close_issue(self):
        if self._validate_answer():
            active_id = self.env.context.get('active_id')
            issue = self.env['project.issue'].browse(active_id)
            vals = {'pergunta1': self.pergunta1,
                    'pergunta2': self.pergunta2,
                    'pergunta3': self.pergunta3,
                    'pergunta4': self.pergunta4,
                    'can_close': True,
                    'stage_id': STAGE_ID_CLOSED}
            issue.write(vals)

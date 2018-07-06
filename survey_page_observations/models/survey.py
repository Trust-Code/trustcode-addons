from odoo import fields, models


class SurveyPage(models.Model):
    _inherit = 'survey.page'

    page_description = fields.Text(string="Descrição da página")


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    question_description = fields.Text(string="Descrição da pergunta")

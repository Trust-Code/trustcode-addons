from odoo import fields, models


class SurveyPage(models.Model):
    _inherit = 'survey.page'

    observations = fields.Text()


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    observations = fields.Text()

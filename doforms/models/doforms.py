# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class DoForms(models.Model):
    _name = 'doforms'
    _inherit = ['mail.thread', 'ir.needaction_mixin', 'utm.mixin']
    _description = u'Modulo Básico para Formulários'

    name = fields.Char()
    origin = fields.Char(string="Origem")
    stage_id = fields.Many2one('doforms.stage', string=u'Situações')

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('doforms')
        vals.update({'name': sequence})
        return super(DoForms, self).create(vals)


class DoFormsStage(models.Model):
    _name = 'doforms.stage'
    _description = u'Estágio para Formulários'

    name = fields.Char(string='Name')

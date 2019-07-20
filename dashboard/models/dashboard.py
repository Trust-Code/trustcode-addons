# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class Dashboard(models.Model):
    _name = 'dashboard'

    @api.one
    def _kanban_dashboard_graph(self):
        space = {'self': self}
        exec(self.code, space)
        self.dashboard_graph = space['result']

    identifier = fields.Char(string="Identificador", size=60)
    name = fields.Char(string="Descrição")
    code = fields.Text(string="Código")
    size = fields.Selection(
        [('one', '25%'), ('two', '50%'), ('three', '75%'),
         ('four', '100%')], string="Tamanho", default="four")

    dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')

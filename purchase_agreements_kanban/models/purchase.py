# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime
from dateutil.parser import parse

class PurchaseAgreementsKanban(models.Model):
    _inherit = 'purchase.requisition'

    sequence =fields.Integer(string="Kanban Sequece")
    state_kanban = fields.Selection([
        	('req','Requisição de Compras'),
            ('req_pdc','Requisição de Compras em PDC'),
            ('req_concl','Requisição de Compras Conluída'),
            ('req_fat','À Faturar'),
            ('req_fin','Finalizado'),
            ],
            string='Status Kanban',
            index=True,
            copy=False,
            default='req',
            track_visibility='onchange')

    image=fields.Many2one(
        compute="_get_image",
        comodel_name="ir.attachment",
        ondelete="set null")

    days_end=fields.Integer(string="End Date in Days", compute="_get_days")
    days_ordering=fields.Integer(string="Ordering in Days")
    days_delivery=fields.Integer(string="Delivery in Days")

    @api.depends('state_kanban')
    def _get_sequence(self):
        dict_seq = []
            ['req','date_end asc',1000],
            ['req_pdc','date_end asc',1000],
            ]
        for seq in dict_seq:
            seq_state = self.search(
                [('state_kanban','in',[seq[0]])], order=seq[1])

            for rec in seq_state:
                rec.sequence = seq[2]
                seq[2] +=1



            elif rec.state_kanban == 'req_pdc':

    @api.depends('account_analytic_id')
    def _get_image(self):
        obj_attach = self.env['ir.attachment']
        obj_project = self.env['project.project']
        for rec in self:
            project_id=obj_project.search(
                [('analytic_account_id','=',rec.account_analytic_id.id)],
                 limit=1)
            attach_id = obj_attach.search(
                [('res_model','=','project.project'),
                 ('res_id','=',project_id.id)],
                 limit=1)
            if attach_id:
                rec.image=attach_id

    @api.depends('date_end')
    def _get_days(self):
        for rec in self:
            if rec.date_end:
                rec.days_end=(datetime.now() - parse(rec.date_end)).days

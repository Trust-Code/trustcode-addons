# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, date
from dateutil import parser

class PurchaseAgreementsKanban(models.Model):
    _inherit = 'purchase.requisition'

    sequence=fields.Integer(store=True)
    state_kanban=fields.Selection([
        	('req','Requisição de Compras'),
            ('req_pdc','Requisição em PDC'),
            ('req_concl','Requisição Concluída'),
            ('req_fat','À Faturar'),
            ('req_fin','Finalizado'),
            ],
            string='Status Kanban',
            compute='_get_state_kanban',
            store=True,
            index=True,
            copy=False,
            default='req',
            track_visibility='onchange')
    image=fields.Many2one(
        compute="_get_image",
        comodel_name="ir.attachment",
        ondelete="set null")
    days_end=fields.Integer(string="End Date in Days", store=True)
    days_ordering=fields.Integer(string="Ordering in Days", store=True)
    days_schedule=fields.Integer(string="Delivery in Days", store=True)

    @api.multi
    def write(self,vals):
        seq_dict = {
            'req':['date_end','asc'],
            'req_pdc':['ordering_date','asc'],
            'req_concl':['schedule_date','desc'],
            'req_fat':['schedule_date','asc'],
            'req_fin':['schedule_date','desc'],
            }
        seq_col = seq_dict[self.state_kanban]
        seq_ids = self.search(
            [('state_kanban','in',[self.state_kanban])],
            order=seq_col[0]+' '+seq_col[1],
            limit=3)
        for id in seq_ids:
            if seq_col[1] == 'desc':
                if self[seq_col[0]] < id[seq_col[0]]:
                    vals['sequence']=1
                    continue
            else:
                if self[seq_col[0]] > id[seq_col[0]]:
                    vals['sequence']=1
                    continue
        return super(PurchaseAgreementsKanban,self).write(vals)

    @api.depends('purchase_ids','order_count','state','purchase_ids.state')
    def _get_state_kanban(self):
        for rec in self:
            purchase_ids = rec.env['purchase.order'].search(
                                [('requisition_id','=',rec.id)])
            if rec.state in ['draft','in_progress','open']:
                rec.state_kanban = 'req'
            if rec.state in ['draft','in_progress','open'] and purchase_ids:
                rec.state_kanban = 'req_pdc'
            if purchase_ids:
                for id in purchase_ids:
                    if id.state in ['purchase']:
                        rec.state_kanban = 'req_fat'
            if purchase_ids:
                for id in purchase_ids:
                    if id.state in ['done']:
                        rec.state_kanban = 'req_fin'
            if rec.state in ['done']:
                rec.state_kanban = 'req_concl'

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

    @api.onchange('date_end','ordering_date','schedule_date')
    def _onchange_days(self):
        if self.date_end:
            self.days_end=self._days(self.date_end)
        if self.ordering_date:
            self.days_ordering=self._days(self.ordering_date)
        if self.schedule_date:
            self.days_schedule=self._days(self.schedule_date)

    def _days(self,date_from):
        return ((parser.parse(date_from)).date() - date.today()).days

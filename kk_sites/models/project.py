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
    art = fields.Char('ART', compute='_compute_art', store=True, readonly=False)
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

    @api.multi
    @api.depends('sale_line_id', 'sale_line_id.price_total')
    def _compute_art(self):
        for project in self:
            if project.sale_line_id and not project.sale_line_id.price_total:
                project.update({'art': 'N/E'})


class Task(models.Model):
    _inherit = 'project.task'

    kk_site_id = fields.Many2one(
        'kk.sites',
        string="Site",
        store=True)

    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order", string="Pedido de Compra"
    )
    kk_delivery_date = fields.Date(string="Data de Entrega 3º")
    kk_po_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Fornecedor Relacionado",
        store=True
    )

    @api.onchange('purchase_order_id')
    def onchange_purchase_order_id(self):
        for task in self:
            task.kk_po_partner_id = task.purchase_order_id.partner_id.id

    @api.model
    def create(self, vals):
        project = self.env['project.project'].browse(vals['project_id'])
        if not vals.get('kk_site_id'):
            vals.update({'kk_site_id': project.kk_site_id.id})
        res = super(Task, self).create(vals)
        res._set_po_delivery_date()
        if vals.get('stage_id'):
            res.update_date_delivered(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(Task, self).write(vals)
        if vals.get('stage_id'):
            self.update_date_delivered(vals)
        self._set_po_delivery_date()
        return res

    def update_date_delivered(self, vals):
        stages_done = self.env['project.task.type'].search(
            [('is_done', '=', True)])
        value = False
        if all(tasks.stage_id.id in stages_done.ids for tasks in
               self.project_id.task_ids):
            value = datetime.datetime.now()
        self.project_id.date_delivered = value

    @api.multi
    def _set_po_delivery_date(self):
        for item in self:
            if item.kk_delivery_date and item.purchase_order_id:
                item.purchase_order_id.order_line.write(
                    {"kk_delivery_date": item.kk_delivery_date}
                )


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_done = fields.Boolean('Concluído')

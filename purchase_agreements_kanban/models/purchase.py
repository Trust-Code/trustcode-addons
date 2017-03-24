# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Lan, Trustcode
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class PurchaseAgreementsKanban(models.Model):
    _inherit = 'purchase.requisition'

    state_kanban = fields.Selection([
        	('req','Requisição de Compras'),
            ('rep_pdc','Requisição de Compras em PDC'),
            ('req_concl','Requisição de Compras Conluída'),
            ('req_fat','À Faturar'),
            ('req_fin','Finalizado'),
            ],
            string='Status Kanban',
            index=True,
            copy=False,
            default='req',
            track_visibility='onchange')

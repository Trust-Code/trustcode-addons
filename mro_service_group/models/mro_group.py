# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    mro_group_id = fields.Many2one('mro.group', string=u'Agrupador')

    @api.onchange('purchase_id')
    def _mro_group_purchase_order_change(self):
        self.mro_group_id = self.purchase_id.mro_group_id


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mro_group_id = fields.Many2one('mro.group', string=u'Agrupador')
    maintenance_count = fields.Integer(
        'Maintenance', compute='_compute_maintenance_count')

    def _compute_maintenance_count(self):
        for item in self:
            total = self.env['mro.order'].search_count([
                ('sale_order_id', '=', item.id)])
            item.delivery_count = total

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.mro_group_id:
            res['mro_group_id'] = self.mro_group_id.id
        return res

    @api.multi
    def action_view_mro(self):
        maintenances = self.env['mro.order'].search([
            ('sale_order_id', '=', self.id)])
        action = self.env.ref('mro.action_orders').read()[0]
        if len(maintenances) > 1:
            action['domain'] = [('id', 'in', maintenances.ids)]
        elif len(maintenances) == 1:
            action['views'] = [(self.env.ref('mro.mro_order_form_view').id,
                                'form')]
            action['res_id'] = maintenances.ids[0]
        else:
            action['domain'] = [('id', '=', 0)]
        action['context'] = {'default_sale_order_id': self.id,
                             'default_mro_group_id': self.mro_group_id.id}
        return action


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    mro_group_id = fields.Many2one('mro.group', string=u'Agrupador')


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    mro_group_id = fields.Many2one('mro.group', string=u'Agrupador')

    def handle_partner_assignation(self, action, partner_id):
        res = super(CrmLead, self).handle_partner_assignation(
            action, partner_id)
        for item in self:
            if item.mro_group_id:
                item.mro_group_id.partner_id = res[item.id]
        return res


class MroOrder(models.Model):
    _inherit = 'mro.order'

    mro_group_id = fields.Many2one('mro.group', string=u'Agrupador')
    sale_order_id = fields.Many2one('sale.order', string=u'Pedido de Venda')
    order_line_id = fields.Many2one(
        'sale.order.line', string=u'Linha do Pedido')

    @api.onchange('sale_order_id')
    def _onchange_sale_order(self):
        self.mro_group_id = self.sale_order_id.mro_group_id

    def _prepare_procurement_values(self, group, order, line):
        vals = super(MroOrder, self)._prepare_procurement_values(
            group, order, line)
        if self.mro_group_id:
            vals['mro_group_id'] = self.mro_group_id.id
        return vals

    def action_confirm(self):
        res = super(MroOrder, self).action_confirm()
        for order in self:
            order.procurement_group_id.mro_group_id = order.mro_group_id
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    mro_group_id = fields.Many2one('mro.group', string=u'Agrupador')

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        if self.mro_group_id:
            vals['mro_group_id'] = self.mro_group_id.id
        return vals


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mro_group_id = fields.Many2one('mro.group', string=u'Agrupador')


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    mro_group_id = fields.Many2one('mro.group', string=u'Agrupador')

    @api.multi
    def _prepare_purchase_order(self, partner):
        vals = super(ProcurementOrder)._prepare_purchase_order(partner)
        if self.mro_group_id:
            vals['mro_group_id'] = self.mro_group_id.id
        return vals

    def _get_stock_move_values(self):
        vals = super(ProcurementOrder, self)._get_stock_move_values()
        if self.mro_group_id:
            vals['mro_group_id'] = self.mro_group_id.id
        return vals


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    mro_group_id = fields.Many2one('mro.group', string=u'Agrupador')


class MroGroup(models.Model):
    _name = 'mro.group'
    _description = u'Agrupador de serviço'

    name = fields.Char(string="Nome", size=60)
    partner_id = fields.Many2one('res.partner', string=u"Cliente")
    asset_id = fields.Many2one('asset.asset', string=u"Equipamento")

    maintenance_order_ids = fields.One2many(
        'mro.order', 'mro_group_id', string=u"Ordens de Manutenção")
    lead_ids = fields.One2many(
        'crm.lead', 'mro_group_id', string=u"Oportunidades")
    sale_order_ids = fields.One2many(
        'sale.order', 'mro_group_id', string=u"Vendas")
    purchase_order_ids = fields.One2many(
        'purchase.order', 'mro_group_id', string=u"Compras")
    picking_ids = fields.One2many(
        'stock.picking', 'mro_group_id', string=u"Recebimento de Compras")
    customer_invoice_ids = fields.One2many(
        'account.invoice', 'mro_group_id', string=u"Faturas de Cliente",
        domain=[('type', 'in', ('out_invoice', 'out_refund'))])
    supplier_invoice_ids = fields.One2many(
        'account.invoice', 'mro_group_id', string=u"Faturas de Fornecedor",
        domain=[('type', 'in', ('in_invoice', 'in_refund'))])

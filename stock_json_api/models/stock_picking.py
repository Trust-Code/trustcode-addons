# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    amount_total = fields.Float(string="Valor Total", readonly=True)

    discount = fields.Float(string='Desconto')

    transporte = fields.Float(string='Transporte')

    embalagem = fields.Float(string='Embalagem')

    caixa = fields.Boolean(string='Caixa')
    cesta = fields.Boolean(string='Cesta')
    sacola = fields.Boolean(string='Sacola')
    caixa_ovo = fields.Boolean(string='Caixa de Ovo')
    morango = fields.Boolean(string='Morango')
    cesta_retornavel = fields.Boolean(string='Cesta Retornável')

    rota = fields.Char(string="ROTA")
    transportadora = fields.Char(string="Transportadora")
    motorista = fields.Char(string="Motorista")
    placa = fields.Char(string="Placa")
    volumes = fields.Char(string="Volumes")

    def create_new_picking(self, picking_ids):
        for picking in picking_ids:
            if picking.picking_type_id.next_picking_type_id:
                picking_type_id = picking.picking_type_id.next_picking_type_id
                new_picking = picking.copy()
                new_picking.write({
                    'picking_type_id': picking_type_id.id
                })

    @api.multi
    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        if self.state == 'done':
            self.create_new_picking(self)

        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    valor_bruto = fields.Float(string="Valor bruto", readonly=True)
    price_unit = fields.Float(
        string="Preço Unitário",
        readonly=True,
        compute='_compute_price_unit')

    @api.depends('valor_bruto', 'product_uom_qty')
    def _compute_price_unit(self):
        for item in self:
            if not item.price_unit:
                item.price_unit = item.valor_bruto/item.product_uom_qty


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        res = super(StockImmediateTransfer, self).process()
        self.env['stock.picking'].create_new_picking(self.pick_ids)
        return res


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process(self):
        res = super(StockBackorderConfirmation, self).process()
        self.env['stock.picking'].create_new_picking(self.pick_ids)
        return res

    def process_cancel_backorder(self):
        res = super(
            StockBackorderConfirmation, self).process_cancel_backorder()
        self.env['stock.picking'].create_new_picking(self.pick_ids)
        return res

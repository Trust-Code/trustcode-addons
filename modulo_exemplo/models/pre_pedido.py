

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class PrePedido(models.Model):
    _name = 'pre.pedido'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(string="Numero do pedido")

    state = fields.Selection(
        [('draft', 'Provisório'), ('done', 'Confirmado')],
        string="Situação", default='draft')

    partner_id = fields.Many2one("res.partner", string="Cliente")
    currency_id = fields.Many2one('res.currency')
    
    desconto = fields.Monetary(string="Desconto total", compute='_compute_totais', store=True)
    valor_total = fields.Monetary(string="Valor total", compute='_compute_totais', store=True)
    
    item_ids = fields.One2many("pre.pedido.item", "pedido_id", string="Itens do Pedido")
    
    desconto_no_total = fields.Monetary(string="Aplicar desconto")
    novo_valor_total = fields.Monetary(string="Novo Valor total")

    @api.onchange('desconto_no_total')
    def _onchange_desconto_no_total(self):
        for item in self:
            desconto = item.desconto_no_total 
            
            if desconto <= 0 or len(item.item_ids) == 0:
                continue
            
            rateio = desconto / len(item.item_ids)
            for line in item.item_ids:
                line.desconto += rateio
                
            item.desconto_no_total = 0

    @api.onchange('novo_valor_total')
    def _onchange_novo_valor_total(self):
        for item in self:
            desconto = item.valor_total - item.novo_valor_total 
            
            if desconto <= 0 or len(item.item_ids) == 0:
                continue
            
            rateio = round(desconto / len(item.item_ids), 2)
            resto = desconto
            for line in item.item_ids:
                line.desconto += rateio
                resto -= desconto

            # seta o resto no ultimo elemento para dar certo
            item.item_ids[-1].desconto += resto
            item.novo_valor_total = 0

    @api.depends('item_ids', 'item_ids.total')
    def _compute_totais(self):
        for item in self:
            item.desconto = sum([x.desconto for x in item.item_ids])
            item.valor_total = sum([x.total for x in item.item_ids])
    
    
    def action_cancel_document(self):
        self.write({'state': 'draft'})
        
    def action_confirm_document(self):
        self.write({'state': 'done'})

class PrePedidoItem(models.Model):
    _name = 'pre.pedido.item'
    
    name = fields.Char(string="Item")

    product_id = fields.Many2one('product.product', string="Produto")
    currency_id = fields.Many2one('res.currency', "Moeda")
    
    pedido_id = fields.Many2one('pre.pedido', string="Pedido")

    quantidade = fields.Float(string="Quantidade")
    preco_unitario = fields.Float(string="Preço Unitário")
    desconto = fields.Monetary(string="Desconto")
    subtotal = fields.Monetary(string="SubTotal", compute='_compute_total_item', store=True)
    total = fields.Monetary(string="Total", compute='_compute_total_item', store=True)


    @api.constrains('quantidade', 'preco_unitario', 'desconto')
    def validate_values_item(self):
        for item in self:
            if item.quantidade <= 0:
                raise ValidationError('Quantidade deve ser maior que 0')
            if item.preco_unitario <= 0:
                raise ValidationError('Preço deve ser maior que 0')
            if item.desconto > (item.quantidade * item.preco_unitario):
                raise ValidationError('O desconto deve ser menor que o valor dos produtos')


    @api.onchange('product_id')
    def _onchange_product_id(self):
        for item in self:
            item.preco_unitario = item.product_id.lst_price

    @api.depends('quantidade', 'preco_unitario', 'desconto')
    def _compute_total_item(self):
        for item in self:
            item.subtotal = round(item.quantidade * item.preco_unitario, 2)
            item.total = round((item.quantidade * item.preco_unitario) - item.desconto, 2)
    


    

    
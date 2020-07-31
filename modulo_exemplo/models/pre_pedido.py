

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class PrePedido(models.Model):
    _name = 'pre.pedido'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(string="Numero do pedido")

    state = fields.Selection(
        [('draft', 'Provisório'), ('done', 'Confirmado')],
        string="Situação", default='draft', track_visibility='always')

    partner_id = fields.Many2one("res.partner", string="Cliente")
    currency_id = fields.Many2one('res.currency')
    
    desconto = fields.Monetary(string="Desconto total", compute='_compute_totais', store=True)
    valor_total = fields.Monetary(string="Valor total", compute='_compute_totais', store=True)
    
    item_ids = fields.One2many("pre.pedido.item", "pedido_id", string="Itens do Pedido")
    
    desconto_no_total = fields.Monetary(string="Aplicar desconto")
    novo_valor_total = fields.Monetary(string="Novo Valor total")

    sale_order_count = fields.Integer(compute='compute_sale_order')
    
    order_ids = fields.One2many('sale.order', 'pre_pedido_id')

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

    def compute_sale_order(self):
        for pre in self:
            pre.sale_order_count = self.env['sale.order'].search_count(
                [('pre_pedido_id', '=', pre.id)])

    @api.depends('item_ids', 'item_ids.total')
    def _compute_totais(self):
        for item in self:
            item.desconto = sum([x.desconto for x in item.item_ids])
            item.valor_total = sum([x.total for x in item.item_ids])
    
    
    def action_cancel_document(self):
        self.order_ids.filtered(lambda x: x.state in ('draft', 'sent')).action_cancel()
        self.write({'state': 'draft'})

    
    def _prepare_sale_order(self):
        items = []
        for line in self.item_ids:
            vals = line._prepare_sale_order_item()
            items.append((0, None, vals))
            
        return {
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'order_line': items,
            'pre_pedido_id': self.id,
        }
    
    def action_confirm_document(self):
        
        for pre in self:
            vals = pre._prepare_sale_order()
            order = self.env['sale.order'].create(vals)
            
            message = "Este pedido foi criado a partir de: <a href=# data-oe-model=pre.pedido data-oe-id=%d>%s</a><br>" % (pre.id, pre.name)
            order.message_post(body=message)

        self.write({'state': 'done'})
        
    def action_view_orders(self):    
        if self.sale_order_count == 1:
            # Buscando a referencia para a ação
            dummy, act_id = self.env['ir.model.data'].get_object_reference(
                'sale', 'action_quotations_with_onboarding')
            # buscando a referencia para o formulario que vai abrir
            dummy, view_id = self.env['ir.model.data'].get_object_reference(
                'sale', 'view_order_form')

            # aqui eu modifico a view da ação
            vals = self.env['ir.actions.act_window'].browse(act_id).read()[0]
            vals['view_id'] = (view_id, 'sale.order.form')
            vals['views'][1] = (view_id, 'form')
            vals['views'] = [vals['views'][1], vals['views'][0]]

            # aqui eu vou buscar o id do pedido que precisa abrir
            order = self.env['sale.order'].search(
                [('pre_pedido_id', '=', self.id)], limit=1)
    
            vals['res_id'] = order.id
            return vals
        else:
            dummy, act_id = self.env['ir.model.data'].get_object_reference(
                    'sale', 'action_quotations_with_onboarding')
            vals = self.env['ir.actions.act_window'].browse(act_id).read()[0]
            vals['domain'] = [('pre_pedido_id', '=', self.id)]
            vals['context'] = {}
            return vals

        

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
    
    def _prepare_sale_order_item(self):
        return {
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantidade,
            'price_unit': self.total / self.quantidade,
        }
    

    
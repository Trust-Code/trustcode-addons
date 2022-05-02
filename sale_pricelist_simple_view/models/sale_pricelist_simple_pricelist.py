#-*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api


class Sale_pricelist_simple_view(models.Model):
    _inherit = 'product.pricelist'

    show_list = fields.Boolean("Exibir Lista")
    color_id = fields.Many2many(
        'product.pricelist.tag', string="Cor atribuida", required=True)

    def change_pricelist_product(self):
        self.env['product.template'].change_pricelist_cron()

    @api.onchange('color_id')
    @api.depends('color_id')
    def change_colors(self):
        if len(self.color_id) > 1:
                raise ValidationError("Apenas uma cor pode ser Atribuida!")


class Sale_pricelist_simple_view_product_line(models.Model):
    _name = 'product.pricelist.line'

    product_id = fields.Many2one('product.template', string='Produto')
    pricelist_ids = fields.Many2one(
        'product.pricelist', string='Lista de Preços')
    price_required = fields.Float(string="Preço")
    color = fields.Integer()
    show_list = fields.Boolean(string="Exibir Lista")

    def name_get(self):
        result = []
        for record in self:
            name = str(record.pricelist_ids.currency_id.symbol) + str(
                round(record.price_required, 2)).replace(".", ",") + "0"
            result.append((record.id, name))
        return result


class Sale_pricelist_simple_view_color(models.Model):
    _name = 'product.pricelist.tag'

    name = fields.Char(string="Nome")
    color = fields.Integer(string="Índice de Cores", default=10)

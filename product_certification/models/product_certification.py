# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductCertification(models.Model):
    _name = 'product.certification'

    product_tmpl_id = fields.Many2one('product.template', string='Produto')
    certifying_entity = fields.Char('Entidade Certificadora')
    certificate_date = fields.Date('Data da Certificação')
    certificate_number = fields.Char('Número da Certificação')
    certificate_expiration_date = fields.Date(
        'Data de Expiração do Certificado')

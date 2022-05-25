from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Segmento(models.Model):
    _name= 'partner.segment'
    name = fields.Char(string ='Nome')

class Platforma(models.Model):
    _name= 'partner.platform'
    name = fields.Char(string ='Nome')

class Suporte(models.Model):
    _name= 'partner.support'
    name = fields.Char(string ='Nome')

class ResPartner(models.Model):
    _inherit = ['res.partner']

    estrategia = fields.Selection(
        [('nao_atender', 'Não atender'),('atender', 'Atender')],
        string='Estratégia',
        default='atender',
        required=False
        )
    perfil_suporte_id = fields.Many2one('partner.support',string='Perfil do Suporte')#Perfil do suporte
    br_account_cnae_id = fields.Many2one('br_account.cnae', string='CNAE Principal')
    equipamento_ids = fields.Many2many('product.template', string='Equipamentos utilizados')#Equipamentos utilizados
    segmento_ids = fields.Many2many('partner.segment',string='Segmento')#Segmento
    plataforma_id = fields.Many2one('partner.platform',string='Plataforma')#Plataforma

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        """ Returns the list of fields that are managed by the commercial entity
        to which a partner belongs. These fields are meant to be hidden on
        partners that aren't `commercial entities` themselves, and will be
        delegated to the parent `commercial entity`. The list is meant to be
        extended by inheriting classes. """
        return res + ["estrategia", "perfil_suporte_id", "br_account_cnae_id", "equipamento_ids", "segmento_ids", "plataforma_id"]

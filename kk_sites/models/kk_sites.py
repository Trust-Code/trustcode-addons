# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class KKSites(models.Model):
    _name = 'kk.sites'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    cod_site_kk = fields.Char(
        string="Código do Site: ",
        required=True,
        track_visibility='always')

    partner_id = fields.Many2one(
        'res.partner',
        string="Cliente",
        required=True,
        track_visibility='onchange')

    site_id = fields.Char(
        string="ID do Site: ",
        required=True,
        track_visibility='onchange')

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(string='CEP')
    city_id = fields.Many2one(
        'res.state.city',
        string="Cidade",
        track_visibility='onchange')
    state_id = fields.Many2one(
        "res.country.state",
        string='Estado',
        ondelete='restrict',
        required=True,
        track_visibility='onchange')
    country_id = fields.Many2one(
        'res.country',
        string='País',
        ondelete='restrict',
        required=True)
    number = fields.Char(string='Número')

    referencia = fields.Char(string="Referência")

    coordenadas = fields.Char(
        string="Coodenadas em graus decimais (Latitude, Longitude)")

    tipo_acesso = fields.Char(string="Tipo de Acesso")

    local_retirada_chave = fields.Char(string='Local de Retirada da Chave')

    tipo_site = fields.Selection(
        [
            ('greenfield', 'Greenfield'),
            ('indoor', 'Indoor'),
            ('rooftop', 'Roof Top'),
            ('tunel', 'Túnel')
        ],
        string="Tipo de Site"
    )

    tipo_estrutura = fields.Selection(
        [
            ('cavalete_auto', 'Cavalete Metálico Autoportante'),
            ('cavalete_estaiado', 'Cavalete Metálico Estaiado'),
            ('fast_size', 'Fast Site'),
            ('mastro_metalico', 'Mastro Metálico'),
            ('poste_concreto', 'Poste de Concreto'),
            ('poste_madeira', 'Poste de Madeira'),
            ('poste_metalico', 'Poste Metálico'),
            ('torre_concreto', 'Torre de Concreto'),
            ('torre_auto', 'Torre Metálica Autoportante'),
            ('torre_estaiada', 'Torre Metálica Estaiada'),
            ('poste_torre', 'Poste Metálico + Torre Metálica Autoportante')

        ],
        string="Tipo de Estrutura"
    )

    secao_transversal = fields.Selection(
        [
            ('circular', 'Circular'),
            ('dodecagonal', 'Dodecagonal'),
            ('quadrada', 'Quadrada'),
            ('triangular', 'Triangular'),
            ('triangular_quadrada', 'Triangular + Quadrada'),
            ('retangular', 'Retangular'),
        ],
        string="Seção Transversal EV"
    )

    fabricante_id = fields.Many2one(
        'res.partner', string="Fabicante da EV")

    modelo = fields.Char('Modelo EV')

    altura_total = fields.Float('Altura Total EV (m)')

    ampliada = fields.Boolean('EV Ampliada?')

    abertura_base = fields.Integer('Abertura da Base (mm)')

    perfil_montante = fields.Selection(
        [
            ('cantoneira', 'Cantoneira (L)'),
            ('cantoneira_dobrada', 'Cantoneira Dobrada 60º (S)'),
            ('dobrada_l', 'Cantoneira Dobrada 60º (S) + Cantoneira (L)'),
            ('dobrada_dubla', 'Cantoneira Dobrada 60º Dupla (2S)'),
            ('cantoneira_dupla', 'Cantoneira Dupla (2L)'),
            ('chapa_dobrada', 'Chapa Dobrada (V)'),
            ('chapa_dob_cant_l', 'Chapa Dobrada (V) + Cantoneira (L)'),
            ('chapa_dob_cant_dob', 'Chapa Dobrada (V) +\
                 Cantoneira Dobrada 60º (S)'),
            ('chapa_dob_omega', 'Chapa Dobrada (V) + Ômega (O)'),
            ('omega', 'Ômega (O)'),
            ('omega_dupla', 'Ômega Dupla (2O)'),
            ('tubular', 'Tubular (TB)'),
            ('tubular_cantoneira', 'Tubular (TB) + Cantoneira (L)'),
            ('perfil_u', 'Perfil U (U)'),
            ('barra_redonda_macica', 'Barra Redonda Maciça (BR)')
        ],
        string='Perfil do Montante EV')

    tipo_fundacao = fields.Selection(
        [
            ('estaca_raiz', 'Estaca Raiz'),
            ('estaca_raiz_tirantes', 'Estaca Raiz + Tirantes'),
            ('chapa_metal', 'Chapa Metálica'),
            ('estaca_metal', 'Estaca Metálica'),
            ('estaca_raiz', 'Estaca Raiz'),
            ('estacao', 'Estacão'),
            ('raider', 'Radier'),
            ('sapata', 'Sapata'),
            ('tirante', 'Tirante'),
            ('tubo_metalico', 'Tubo Metálico'),
            ('tubulao', 'Tubulão'),
            ('tubulao_estaca', 'Tubulão + Estaca'),
            ('viga', 'Viga'),
        ],
        string="Tipo de Fundação")

    dimensoes_fundacao = fields.Char(string="Dimensões da Fundação (cm x cm)")

    profundidade_fundacao = fields.Integer(
        string='Profundidade da Fundação (cm)')

    notes = fields.Text("Observações")

    pasta_servidor = fields.Char(
        string="Pasta no Servidor",
        track_visibility='onchange')

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            return {'domain': {'state_id': [(
                'country_id', '=', self.country_id.id)]}}
        else:
            return {'domain': {'state_id': []}}

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            return {'domain': {'city_id': [(
                'state_id', '=', self.state_id.id)]}}
        else:
            return {'domain': {'city_id': []}}

    def _mask_dimensoes_fundacao(self, dimensoes):
        dimensoes = dimensoes.strip()
        try:
            dim = dimensoes.split('x')
            if len(dim) != 2:
                dim = dimensoes.split(' ')
            if len(dim) != 2:
                dim = dimensoes.split('-')
            if len(dim) != 2:
                raise Exception
            comprimento, largura = [int(item.strip()) for item in dim]
            return '{} x {}'.format(comprimento, largura)
        except Exception:
            raise ValidationError(
                "Verifique se as dimensões da fundação são válidas.\
                    \n Formato padrão: XXX x XXX")

    def _mask_coordenadas(self, coord):
        coord = coord.split(',')
        if len(coord) > 2:
            raise ValidationError(
                "Use ponto para delimitar casas decimais no campo coordenadas.\
                \n Formato padrão: -XX.XXXXX, -XX.XXXXX")
        try:
            coord = [float(item.strip()) for item in coord]
            return '{}, {}'.format(coord[0], coord[1])
        except Exception:
            raise ValidationError("Verifique se as coordenadas são válidas.\
                Formato padrão: -XX.XXXXX, -XX.XXXXX")

    @api.multi
    def write(self, vals):
        if vals.get('coordenadas'):
            vals['coordenadas'] = self._mask_coordenadas(vals['coordenadas'])
        if vals.get('dimensoes_fundacao'):
            vals['dimensoes_fundacao'] = self._mask_dimensoes_fundacao(
                vals['dimensoes_fundacao'])
        return super(KKSites, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('coordenadas'):
            vals['coordenadas'] = self._mask_coordenadas(vals['coordenadas'])
        if vals.get('dimensoes_fundacao'):
            vals['dimensoes_fundacao'] = self._mask_dimensoes_fundacao(
                vals['dimensoes_fundacao'])
        return super(KKSites, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.street = self.partner_id.street
        self.street2 = self.partner_id.street2
        self.zip = self.partner_id.zip
        self.city_id = self.partner_id.city_id
        self.state_id = self.partner_id.state_id
        self.country_id = self.partner_id.country_id
        self.number = self.partner_id.number

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s - %s" % (
                rec.cod_site_kk, rec.partner_id.name or '')))
        return result

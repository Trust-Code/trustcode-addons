# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class Site(models.Model):
    _name = 'kk.sites'

    cod_site_kk = fields.Char(
        string="Código Site KK",
        required=True)

    partner_id = fields.Many2one(
        'res.partner',
        string="Cliente",
        required=True)

    site_id = fields.Char(
        string="ID do Site",
        required=True)

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one(
        "res.country.state",
        string='State',
        ondelete='restrict',
        required=True)
    country_id = fields.Many2one(
        'res.country',
        string='Country',
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
        'site.fabricante.torre', string="Fabicante da EV")

    modelo = fields.Char('Modelo EV')

    altura_total = fields.Float('Altura Total EV (m)')

    ampliada = fields.Boolean('EV Ampliada?')

    abertura_base = fields.Float('Abertura da Base (mm)')

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

    profundidade_fundacao = fields.Float(
        string='Profundidade da Fundação (cm)')

    notes = fields.Text("Observações")

    pasta_servidor = fields.Char("Pasta no Servidor")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.street = self.partner_id.street
        self.street2 = self.partner_id.street2
        self.zip = self.partner_id.zip
        self.city = self.partner_id.city
        self.state_id = self.partner_id.state_id
        self.country_id = self.partner_id.country_id
        self.number = self.partner_id.number

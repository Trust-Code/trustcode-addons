# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class Site(models.Model):
    _name = 'site'

    partner_id = fields.Many2one(
        'res.partner',
        string="Cliente",
        required=True)

    site_id = fields.Char(
        string="ID do Site",
        required=True)

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

    fabricante_id = fields.Many2one('fabricante.torre', string="Fabicante")

    modelo = fields.Char('Modelo')

    altura_total = fields.Float('Altura Total')

    ampliada = fields.Boolean('Ampliada')

    abertura_base = fields.Float('Abertura da Base')

    perfil_montante = fields.Char(
        [
            ('cantoneira', 'Cantoneira (L)'),
            ('cantoneira_dobrada', 'Cantoneira Dobrada 60º (S)'),
            ('dobrada_l', 'Cantoneira Dobrada 60º (S) + Cantoneira (L)'),
            ('dobrada_dubla', 'Cantoneira Dobrada 60º Dupla (2S)'),
            ('cantoneira_dupla', 'Cantoneira Dupla (2L)'),
            ('chapa_dobrada', 'Chapa Dobrada (V)'),
            ('chapa_dob_cant_l', 'Chapa Dobrada (V) + Cantoneira (L)'),
            ('chapa_dob_cant_dob', 'Chapa Dobrada (V) + Cantoneira Dobrada 60º (S)'),
            ('chapa_dob_omega', 'Chapa Dobrada (V) + Ômega (O)'),
            ('omega', 'Ômega (O)'),
            ('omega_dupla', 'Ômega Dupla (2O)'),
            ('tubular', 'Tubular (TB)'),
            ('tubular_cantoneira', 'Tubular (TB) + Cantoneira (L)'),
            ('perfil_u', 'Perfil U (U)'),
            ('barra_redonda_macica', 'Barra Redonda Maciça (BR)')

        ]
        string='Perfil do Montante')

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
        string="Tipo de Fundação"
    )

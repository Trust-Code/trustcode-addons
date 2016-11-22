# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from pysigepweb.webservice_atende_cliente import WebserviceAtendeCliente


class ResCompany(models.Model):
    _inherit = "res.company"

#   correio_login = fields.Char(max_length=30, string="Cliente do Correio")
#   correio_password = fields.Char(max_length=30, string="Senha do Correio")
#   num_contrato = fields.Integer(string="Número de Contrato")
#   num_cartao_postagem = fields.Integer(string="Número do cartão de Postagem")
# TODO: Criar gerar_servicos para Producao
    @api.multi
    def gerar_servicos(self):
        ws = WebserviceAtendeCliente('Homologacao')
        cliente = ws.busca_cliente("9912208555", "0057018901", 'sigep',
                                   'n5f9t8')
        servicos = cliente.contratos['9912208555'].\
            cartoes_postagem['0057018901'].servicos_postagem
        services_obj = self.env['mail.services']
        for i, j in servicos.items():
            services_obj.create({'identificador': j.identificador,
                                 'description': j.descricao,
                                 'service_cod': i})

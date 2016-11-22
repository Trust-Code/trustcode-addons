# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from pysigepweb.webservice_atende_cliente import WebserviceAtendeCliente
from openerp import api, fields, models
from openerp.exceptions import Warning as UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    service_id = fields.Many2one('mail.services',
                                 string="Serviço")
    tag_correio = fields.Char(readonly=True, string="Etiqueta de Rastreamento")

    @api.multi
    def gerar_etiqueta(self):
        if not self.service_id:
            raise UserError(
                "É necessário escolher um serviço de envio antes.\n\
                 O mesmo pode ser criado nas configurações da empresa")
        ws = WebserviceAtendeCliente('Homologacao')
        cliente = ws.busca_cliente("9912208555", "0057018901", 'sigep',
                                   'n5f9t8')
        servico_postagem = self.service_id

        mail_tag = ws.\
            solicita_etiquetas(servico_postagem, 1, cliente, 'C')[0].valor
        self.write({'tag_correio': mail_tag})

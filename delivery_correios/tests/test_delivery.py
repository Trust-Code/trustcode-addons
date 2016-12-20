# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini <alessandrofmartini@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestDeliveryCorreios(TransactionCase):

    def setUp(self):
        super(TestDeliveryCorreios, self).setUp()
        correio = {
            'name': 'Correio',
            'correio_login': 'sigep',
            'correio_password': 'n5f9t8',
            'cod_administrativo': '08082650',
            'num_contrato': '9912208555',
            'cartao_postagem': '0057018901',
            'delivery_type': 'correios',
            'mao_propria': 'N',
            'valor_declarado': False,
            'aviso_recebimento': 'N',
            'ambiente': 1,
        }
        self.delivery = self.env['delivery.carrier'].create(correio)
        partner = {
            'name': 'Parceiro 1',
            'company_type': 'person',
            'cnpj_cpf': '515.741.801-93',
            'zip': '27336-400',
        }
        self.partner = self.env['res.partner'].create(partner)
        produto = {
            'name': 'Produto 1',
            'weight': 10,
            'comprimento': 20,
            'altura': 20,
            'largura': 20,
            'list_price': 20,
        }
        self.produto = self.env['product.product'].create(produto)
        sale_order_line = {
            'product_id': self.produto.id,
            'product_uom_qty': 2,
        }
        self.sale_order_line =\
            self.env['sale.order.line'].create(sale_order_line)
        sale_order = {
            'partner_id': self.partner.id,
            'order_line': [(0, 0, sale_order_line)],
            'carrier_id': self.delivery.id,
        }
        self.sale_order = self.env['sale.order'].create(sale_order)

    @patch('odoo.addons.delivery_correios.models.delivery.calcular_preco_prazo')
    @patch('odoo.addons.delivery_correios.models.delivery.check_for_correio_error')
    def test_correios_get_shipping_price_from_so(self, preco, erro):
        erro.return_value = None
        cServico = type('', (), {})()
        cServico.Valor = '42,00'
        preco.return_value = cServico
        self.env['delivery.carrier'].\
            correios_get_shipping_price_from_so([self.sale_order])
        self.assertEqual(self.sale_order.amount_total, 82)

    @patch('odoo.addons.delivery_correios.models.delivery.busca_cliente')
    @patch('odoo.addons.delivery_correios.models.delivery.check_for_correio_error')
    def test_action_get_correio_services(self, services, erro):
        # mock servicos
        servico_1 = type('', (), {})()
        servico_1.servicoSigep = type('', (), {})()
        servico_1.servicoSigep.chancela = type('', (), {})()
        servico_1.servicoSigep.chancela.chancela = 'foobarbazbam'
        servico_1.codigo = '40096'
        servico_1.id = '104625'
        servico_1.descricao = 'Servico 1'
        Services = type('', (), {})()
        Services.contratos = type('', (), {})()
        Services.contratos.cartoesPostagem = type('', (), {})()
        Services.contratos.dataVigenciaInicio = 2015
        Services.contratos.cartoesPostagem.servicos = [servico_1]
        services.return_value = Services
        erro.return_value = None
        self.delivery.action_get_correio_services()
        self.assertTrue(len(self.delivery.service_id) == 3)

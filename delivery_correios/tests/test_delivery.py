# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini <alessandrofmartini@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import namedtuple
from lxml import objectify
from mock import patch

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
        product_uom = {
            'name': 'UOM',
            'category_id': self.env['product.uom.categ'].create(
                {'name': 'Unity'}).id,
            'uom_type': 'reference',
            'active': True,
            'rounding': 0.00100,
        }
        self.product_uom = self.env['product.uom'].create(product_uom)
        produto = {
            'name': 'Produto 1',
            'weight': 10,
            'comprimento': 20,
            'altura': 20,
            'largura': 20,
            'list_price': 20,
            'uom_id': self.product_uom.id,
            'uom_po_id': self.product_uom.id,
        }
        self.produto = self.env['product.product'].create(produto)
        sale_order = {
            'partner_id': self.partner.id,
            'carrier_id': self.delivery.id,
        }
        self.sale_order = self.env['sale.order'].create(sale_order)
        sale_order_line = {
            'product_id': self.produto.id,
            'product_uom_qty': 2,
            'product_uom': self.product_uom.id,
            'order_id': self.sale_order.id,
        }
        self.sale_order_line =\
            self.env['sale.order.line'].create(sale_order_line)
        self.sale_order.write({
            'order_line': [(4, self.sale_order_line.id, 0)],
        })

    @patch('odoo.addons.delivery_correios.models.delivery.check_for_correio_error')
    @patch('odoo.addons.delivery_correios.models.delivery.calcular_preco_prazo')
    def test_correios_get_shipping_price_from_so(self, preco, erro):
        correio_return_xml = """\
<Servicos>
    <cServico>
        <Codigo>41106</Codigo> 
        <Valor>12,80</Valor> 
        <PrazoEntrega>6</PrazoEntrega> 
        <ValorMaoPropria>0,00</ValorMaoPropria> 
        <ValorAvisoRecebimento>2,80</ValorAvisoRecebimento> 
        <ValorValorDeclarado>0,00</ValorValorDeclarado> 
        <EntregaDomiciliar>S</EntregaDomiciliar> 
        <EntregaSabado>N</EntregaSabado> 
        <Erro>0</Erro> 
        <MsgErro /> 
    </cServico>
    <cServico>
        <Codigo>40010</Codigo> 
        <Valor>29,00</Valor> 
        <PrazoEntrega>2</PrazoEntrega> 
        <ValorMaoPropria>0,00</ValorMaoPropria> 
        <ValorAvisoRecebimento>2,80</ValorAvisoRecebimento> 
        <ValorValorDeclarado>0,00</ValorValorDeclarado> 
        <EntregaDomiciliar>S</EntregaDomiciliar> 
        <EntregaSabado>S</EntregaSabado> 
        <Erro>0</Erro> 
        <MsgErro /> 
    </cServico>
</Servicos>"""
        preco.return_value = objectify.fromstring(correio_return_xml)
        erro.return_value = None
        entrega = self.env['delivery.carrier'].create({
            'name': 'Metodo 1',
            'delivery_type': 'correios',
            'margin': 0,
            'integration_level': 'rate_and_ship',
            'correio_login': 'sigep',
            'correio_password': 'n5f9t8',
            'cod_administrativo': '08082650',
            'num_contrato': '9912208555',
            'cartao_postagem': '0057018901',
            'ambiente': 1,
        })
        servico = self.env['delivery.correios.service'].create({
            'ano_assinatura': '2016',
            'name': 'Serviço 1',
            'code': '40215',
            'identifier': 'foo bar baz',
            'delivery_id': entrega.id,
        })
        entrega.write({
            'service_id': servico.id,
        })
        self.sale_order.write({
            'carrier_id': entrega.id
        })
        self.env['delivery.carrier'].\
            correios_get_shipping_price_from_so(self.sale_order)
        self.assertEqual(self.sale_order.amount_total, 82)

    @patch('odoo.addons.delivery_correios.models.delivery.check_for_correio_error')
    @patch('odoo.addons.delivery_correios.models.delivery.busca_cliente')
    def test_action_get_correio_services(self, services, erro):
        # mock servicos
        correio_return_xml = """\
<cliente>
    <cnpj>20535586000104</cnpj>
    <contratos>
        <cartoesPostagem>
            <codigoAdministrativo>08082650</codigoAdministrativo>
            <numero>12345678</numero>
            <servicos>
                <codigo>40096</codigo>
                <descricao>SEDEX - CONTRATO</descricao>
                <id>104625</id>
                <servicoSigep>
                    <chancela>
                        <chancela>/9j/4AAQSkZJRgABAQEBLAEsAAD/2wBDAAIBAQIBAQIC\
AgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcH</chancela>
                    </chancela>
                </servicoSigep>
            </servicos>
        </cartoesPostagem>
        <dataVigenciaInicio>2016</dataVigenciaInicio>
        <codigoDiretoria>10</codigoDiretoria>
    </contratos>
</cliente>"""
        services.return_value = objectify.fromstring(correio_return_xml)
        erro.return_value = None
        self.delivery.action_get_correio_services()
        servicos = self.env['delivery.correios.service'].search([])
        self.assertTrue(len(servicos) == 1,
                        "Número de serviços: %d " % len(servicos))

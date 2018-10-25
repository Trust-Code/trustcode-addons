# © 2018 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from lxml import objectify
from odoo import api, fields, models


def cnpj_cpf_format(cnpj_cpf):
    if len(cnpj_cpf) == 14:
        cnpj_cpf = (cnpj_cpf[0:2] + '.' + cnpj_cpf[2:5] +
                    '.' + cnpj_cpf[5:8] +
                    '/' + cnpj_cpf[8:12] +
                    '-' + cnpj_cpf[12:14])
    else:
        cnpj_cpf = (cnpj_cpf[0:3] + '.' + cnpj_cpf[3:6] +
                    '.' + cnpj_cpf[6:9] + '-' + cnpj_cpf[9:11])
    return cnpj_cpf


class BomImportWizard(models.TransientModel):
    _name = "bom.import.wizard"

    xml_file = fields.Binary(string="Arquivo XML", required=True)

    @api.multi
    def action_import(self):
        xml_file = base64.decodestring(self.xml_file)
        xml = objectify.fromstring(xml_file)

        so_code = str(xml.DADOS_OBRA.CODIGO)
        cnpj_cpf = cnpj_cpf_format(xml.DADOS_CLIENTE.CNPJ_CPF.text)

        order = self.env['sale.order'].search(
            [('name', 'like', so_code[:-3])])
        if order:
            order.name = so_code
        if not order:
            partner_id = self.env['res.partner'].search(
                [('cnpj_cpf', '=', cnpj_cpf)])
            if not partner_id:
                partner_type = 'person' if len(cnpj_cpf) == 14 else 'company'
                state = self.env['res.country.state'].search(
                    [('code', '=', xml.DADOS_CLIENTE.END_UF),
                     ('country_id.code', '=', 'BR')])
                city = self.env['res.state.city'].search(
                    [('name', 'ilike', xml.DADOS_CLIENTE.END_CIDADE),
                     ('state_id', '=', state.id)])
                partner_id = self.env['res.partner'].create({
                    'name': xml.DADOS_CLIENTE.NOME,
                    'cnpj_cpf': cnpj_cpf,
                    'street': xml.DADOS_CLIENTE.END_LOGR,
                    'number': xml.DADOS_CLIENTE.END_NUMERO,
                    'street2': xml.DADOS_CLIENTE.END_COMPL,
                    'district': xml.DADOS_CLIENTE.END_BAIRRO,
                    'city': xml.DADOS_CLIENTE.END_CIDADE,
                    'city_id': city.id,
                    'zip': xml.DADOS_CLIENTE.END_CEP,
                    'state_id': state.id,
                    'company_type': partner_type,
                    'is_company': True if partner_type == 'company' else False,
                    'customer': True,
                })

            order = self.env['sale.order'].create({
                'partner_id': partner_id.id,
                'name': so_code,
            })
        elif order.order_line:
            order.order_line.mapped('mrp_bom_id').unlink()
            order.order_line.unlink()

        line_env = self.env['sale.order.line']
        prod_env = self.env['product.product']
        prod_tmpl_env = self.env['product.template']
        bom_env = self.env['mrp.bom']
        bomline_env = self.env['mrp.bom.line']
        route_manuf_id = self.env.ref('mrp.route_warehouse0_manufacture').id
        route_mto_id = self.env.ref('stock.route_warehouse0_mto').id
        attr_descr = self.env.ref('bom_import.product_attribute').id
        attr_env = self.env['product.attribute.value']

        for tipologia in xml.TIPOLOGIAS.TIPOLOGIA:
            product_tmpl_id = prod_tmpl_env.search(
                [('name', '=', str(tipologia.CODESQD))], limit=1)
            vals = {
                'name': str(tipologia.CODESQD),
                'standard_price': 0.0,
                'list_price': 0.0,
                'default_code': str(tipologia.CODESQD),
                'type': 'product',
                'attribute_line_ids': [(0, 0, {'attribute_id': attr_descr})],
                'route_ids': [(6, None, [route_manuf_id, route_mto_id])],
            }
            if not product_tmpl_id:
                product_tmpl_id = prod_tmpl_env.create(vals)
            # Sempre cadastra um novo produto filho do template acima
            codigo = self.env['ir.sequence'].next_by_code('product.template')
            attr_value = attr_env.create({'attribute_id': attr_descr,
                                          'name': str(tipologia.DESCR)})
            vals = {
                'name': str(tipologia.CODESQD),
                'standard_price': float(tipologia.PRECO_UNIT),
                'default_code': codigo,
                'weight': float(tipologia.PESO_UNIT),
                'type': 'product',
                'attribute_value_ids': [(0, 0, [attr_value])],
                'product_tmpl_id': product_tmpl_id.id,
            }
            product_id = prod_env.create(vals)

            bom_id = bom_env.create({
                'product_tmpl_id': product_id.product_tmpl_id.id,
                'product_qty': 1.0,
                'code': str(tipologia.TIPO),
                'projetista': str(tipologia.PROJETISTA),
                'width': float(tipologia.LARGURA),
                'height': float(tipologia.ALTURA),
                'trat_perf': str(tipologia.TRAT_PERF),
            })

            # O XML possui componentes, perfis e vidros
            if "COMPONENTE" in dir(tipologia.COMPONENTES):
                for comp in tipologia.COMPONENTES.COMPONENTE:
                    raw_id = prod_env.search(
                        [('default_code', '=', str(comp.CODIGO))], limit=1)
                    vals = {
                        'name': str(comp.DESCRICAO),
                        'standard_price': float(comp.CUSTO),
                        'list_price': float(comp.CUSTO),
                        'default_code': str(comp.CODIGO),
                        'type': 'product',
                        'sale_ok': False,
                    }
                    if not raw_id:
                        raw_id = prod_env.create(vals)
                    else:
                        raw_id.write(vals)
                    bomline_env.create({
                        'bom_id': bom_id.id,
                        'product_id': raw_id.id,
                        'product_qty': float(comp.QTDE),
                        'ref': str(comp.REF),
                        'color_code': str(comp.CODIGOCOR),
                        'size': str(comp.TAM),
                        'is_component': True,
                    })

            # Perfis
            if "PERFIL" in dir(tipologia.PERFIS):
                for perfil in tipologia.PERFIS.PERFIL:
                    raw_id = prod_env.search(
                        [('default_code', '=', str(perfil.CODIGO))], limit=1)
                    vals = {
                        'name': str(perfil.DESCRICAO),
                        'standard_price': float(perfil.CUSTO),
                        'list_price': float(perfil.CUSTO),
                        'default_code': str(perfil.CODIGO),
                        'weight': float(perfil.PESO),
                        'type': 'product',
                        'sale_ok': False,
                    }
                    if not raw_id:
                        raw_id = prod_env.create(vals)
                    else:
                        raw_id.write(vals)
                    bomline_env.create({
                        'bom_id': bom_id.id,
                        'product_id': raw_id.id,
                        'product_qty': float(perfil.QTDE),
                        'ref': str(perfil.REF),
                        'trat': str(perfil.TRAT),
                        'left_angle': str(perfil.ANG_ESQ),
                        'right_angle': str(perfil.ANG_DIR),
                        'size': str(perfil.TAM),
                        'is_profile': True,
                    })

            # Vidros
            if "VIDRO" in dir(tipologia.VIDROS):
                for vidro in tipologia.VIDROS.VIDRO:
                    raw_id = prod_env.search(
                        [('default_code', '=', str(vidro.CODIGO))], limit=1)
                    vals = {
                        'name': str(vidro.DESCRICAO),
                        'standard_price': float(vidro.CUSTO),
                        'list_price': float(vidro.CUSTO),
                        'default_code': str(vidro.CODIGO),
                        'type': 'product',
                        'sale_ok': False,
                    }
                    if not raw_id:
                        raw_id = prod_env.create(vals)
                    else:
                        raw_id.write(vals)
                    bomline_env.create({
                        'bom_id': bom_id.id,
                        'product_id': raw_id.id,
                        'product_qty': float(vidro.QTDE),
                        'ref': str(vidro.REF),
                        'height': float(vidro.ALTURA),
                        'width': float(vidro.LARGURA),
                        'surface': str(vidro.SUPERFICIE),
                        'is_glass': True,
                    })

            line_env.create({
                'order_id': order.id,
                'product_id': product_id.id,
                'product_uom_qty': float(tipologia.QTDE),
                'price_unit': float(tipologia.PRECO_UNIT),
                'mrp_bom_id': bom_id.id,
            })

        return {'type': 'ir.actions.act_window_close'}

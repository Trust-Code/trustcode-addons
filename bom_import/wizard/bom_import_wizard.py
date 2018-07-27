# © 2018 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from lxml import objectify
from odoo import api, fields, models


class BomImportWizard(models.TransientModel):
    _name = "bom.import.wizard"

    xml_file = fields.Binary(string="Arquivo XML", required=True)
    create_product = fields.Boolean(string='Criar Produto?')

    @api.multi
    def action_import(self):
        xml_file = base64.decodestring(self.xml_file)
        xml = objectify.fromstring(xml_file)

        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        order = self.env['sale.order'].browse(active_ids)

        line_env = self.env['sale.order.line']
        prod_env = self.env['product.product']
        bom_env = self.env['mrp.bom']
        bomline_env = self.env['mrp.bom.line']
        route_manuf_id = self.env.ref('mrp.route_warehouse0_manufacture').id
        route_mto_id = self.env.ref('stock.route_warehouse0_mto').id

        for tipologia in xml.TIPOLOGIAS.TIPOLOGIA:
            product_id = prod_env.search(
                [('default_code', '=', str(tipologia.CODESQD))], limit=1)
            vals = {
                'name': str(tipologia.DESCR),
                'standard_price': float(tipologia.PRECO_UNIT),
                'list_price': float(tipologia.PRECO_UNIT),
                'default_code': str(tipologia.CODESQD),
                'weight': float(tipologia.PESO_UNIT),
                'type': 'product',
                'route_ids': [(6, None, [route_manuf_id, route_mto_id])],
            }
            if not product_id:
                product_id = prod_env.create(vals)
            else:
                product_id.write(vals)
            bom_id = bom_env.create({
                'product_tmpl_id': product_id.product_tmpl_id.id,
                'product_qty': 1.0,
                'code': str(tipologia.TIPO),
                # projetista ta string...se pa, tem que mudar dps
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
                'price_unit': float(tipologia.PRECO_UNIT)
            })

        return {'type': 'ir.actions.act_window_close'}

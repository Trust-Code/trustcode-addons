from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _generate_raw_moves(self, exploded_lines):

        moves = super(MrpProduction, self)._generate_raw_moves(exploded_lines)

        # Caso não haja atributos no produto, retorna os moves originais.
        if not self.product_id.attribute_value_ids:
            return moves

        # Formar lista de todos os atributos desse template de produto
        atributos = self.env['product.attribute.value']\
            .search([(
                'product_ids.product_tmpl_id', '=', self.product_tmpl_id.id)])

        # Formar uma lista dos nomes dos atributos do produto escolhido
        product_attr_list = list(item.name for item in
                                 self.product_id.attribute_value_ids)

        atributos_dict = {}

        for item in atributos:
            atributos_dict[item.name] = False

        for item in product_attr_list:
            atributos_dict[item] = True

        # Chamada de método que retorna a lista de codigos (default_code)
        # os quais serão usados para procurar os ingredientes e suas
        # respectivas unidades
        lista_codigos = self.bom_id.retorna_lista_codigos(atributos_dict)

        # Iteração de cada cod/qty para criação de um move
        for codigo, quantidade in lista_codigos:

            bom_line = self.env['mrp.bom.line'].browse(0)
            product_id = self.env['product.product'].search(
                [('default_code', '=', codigo)], limit=1)
            line_data = {
                'original_qty': 1.0,
                'product': product_id,
                'parent_line': False,
                'qty': quantidade
            }
            # Criação dos moves com os dados acima.
            # Usado apenas quando há linhas dinamicas a serem adicionadas
            moves += self._generate_dynamic_raw_move(bom_line, line_data)

        return moves

    def _generate_dynamic_raw_move(self, bom_line, line_data):
        quantity = line_data['qty']

        if self.routing_id:
            routing = self.routing_id
        else:
            routing = self.bom_id.routing_id
        if routing and routing.location_id:
            source_location = routing.location_id
        else:
            source_location = self.location_src_id

        original_quantity = self.product_qty - self.qty_produced

        data = {
            'sequence': bom_line.sequence,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'bom_line_id': bom_line.id,
            'product_id': line_data['product'].id,
            'product_uom_qty': quantity,
            'product_uom': line_data['product'].uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or False,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'unit_factor': quantity / original_quantity,
        }
        return self.env['stock.move'].create(data)

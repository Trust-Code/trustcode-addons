from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _generate_raw_moves(self, exploded_lines):

        moves = super(MrpProduction, self)._generate_raw_moves(exploded_lines)

        # Caso não haja atributos no produto, retorna os moves originais.
        if not self.product_id.attribute_value_ids:
            return moves

        # Formar um set dos nomes dos atributos do produto escolhido
        product_attr_set = set(item.name.lower() for item in
                               self.product_id.attribute_value_ids)

        atributos_set = set()

        for item in product_attr_set:
            atributos_set.add(item)

        # Chamada de método que retorna a lista de codigos (default_code)
        # os quais serão usados para procurar os ingredientes e suas
        # respectivas unidades
        lista_codigos = self.bom_id.retorna_lista_codigos(atributos_set)

        # Iteração de cada cod/qty para criação de um move
        for codigo, quantidade in lista_codigos:

            bom_line = self.env['mrp.bom.line'].browse(0)

            # Para evitar erros de typing, usamos o '=ilike', o qual torna
            # a busca por codigo no modo 'case insensitive'
            product_id = self.env['product.product'].search(
                [('default_code', '=ilike', codigo)], limit=1)
            if product_id:
                line_data = {
                    'original_qty': 1.0,
                    'product': product_id,
                    'parent_line': False,
                    'qty': quantidade
                }
                # Criação dos moves com os dados acima.
                # Usado apenas quando há linhas dinamicas a serem adicionadas
                moves += self._generate_dynamic_raw_move(bom_line, line_data)
            else:
                self.message_post(body="ALERTA! O produto com código '%s' \
não foi encontrado!" % (codigo))

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

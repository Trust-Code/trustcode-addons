# -*- coding: utf-8 -*-
# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# © 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from lxml import etree


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Avoid to have 2 times the field product_tmpl_id, as modules like
        sale_stock adds this field as invisible, so we can't trust the order
        of them. We also override the modifiers to avoid a readonly field.
        """
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type != 'form':
            return res  # pragma: no cover
        if 'order_line' not in res['fields']:
            return res  # pragma: no cover
        line_field = res['fields']['order_line']
        if 'form' not in line_field['views']:
            return res  # pragma: no cover
        view = line_field['views']['form']
        eview = etree.fromstring(view['arch'])
        fields = eview.xpath("//field[@name='product_tmpl_id']")
        field_added = False
        for field in fields:
            if field.get('invisible') or field_added:
                field.getparent().remove(field)
            else:
                # Remove modifiers that makes the field readonly
                field.set('modifiers', "")
                field_added = True
        view['arch'] = etree.tostring(eview)
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    order_state = fields.Selection(related='order_id.state', readonly=True)
    # Needed for getting the lang variable for translating descriptions
    partner_id = fields.Many2one(related='order_id.partner_id', readonly=True)

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string='Product Template',
        auto_join=True)
    product_attribute_ids = fields.One2many(
        comodel_name='product.configurator.attribute',
        domain=lambda self: [("owner_model", "=", self._name)],
        inverse_name='owner_id', string='Atributos do Modelo', copy=True)

    @api.multi
    def onchange_product_id_product_configurator_old_api(self, product_id,
                                                         partner_id=None):
        """Method to be called in case inherited model use old API on_change.
        The returned result has to be merged with current 'value' key in the
        regular on_change method, not with the complete dictionary.

        :param product_id: ID of the changed product.
        :return: Dictionary with the changed values.
        """
        res = {}
        if product_id:
            product_obj = self.env['product.product']
            if partner_id:
                partner = self.env['res.partner'].browse(partner_id)
                product_obj = product_obj.with_context(lang=partner.lang)
            product = product_obj.browse(product_id)
            attr_values_dict = product._get_product_attributes_values_dict()
            for val in attr_values_dict:
                val['product_tmpl_id'] = product.product_tmpl_id.id
                val['owner_model'] = self._name
                val['owner_id'] = self.id
            attr_values = [(0, 0, values) for values in attr_values_dict]
            res['product_attribute_ids'] = attr_values
            res['name'] = self._get_product_description(
                product.product_tmpl_id, product,
                product.attribute_value_ids)
        return res

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        new_value = self.onchange_product_id_product_configurator_old_api(
            product_id=self.product_id.id, partner_id=self.partner_id.id)
        value = res.setdefault('value', {})
        value.update(new_value)
        if self.product_id:
            product_obj = self.env['product.product']
            if self.partner_id:
                product_obj = product_obj.with_context(
                    lang=self.partner_id.lang)
            if self.product_id.description_sale:
                value['name'] += '\n' + self.product_id.description_sale
        return res

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        # First, empty current list
        self.product_attribute_ids = [
            (2, x.id) for x in self.product_attribute_ids]
        if not self.product_tmpl_id.attribute_line_ids:
            self.product_id = self.product_tmpl_id.product_variant_ids
        else:
            # if not self.env.context.get('not_reset_product'):
            #    self.product_id = False
            attribute_list = []
            for attribute_line in self.product_tmpl_id.attribute_line_ids:
                attribute_list.append({
                    'attribute_id': attribute_line.attribute_id.id,
                    'product_tmpl_id': self.product_tmpl_id.id,
                    'owner_model': self._name,
                    'owner_id': self.id,
                })
            self.product_attribute_ids = [(0, 0, x) for x in attribute_list]
        # Needed because the compute method is not triggered
        self.product_attribute_ids._compute_possible_value_ids()
        # Restrict product possible values to current selection
        domain = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
        return {'domain': {'product_id': domain}}

    @api.multi
    @api.onchange('product_attribute_ids')
    def onchange_product_attribute_ids(self):
        product_obj = self.env['product.product']
        domain, cont = product_obj._build_attributes_domain(
            self.product_tmpl_id, self.product_attribute_ids)
        if cont:
            products = product_obj.search(domain)
            # Filter the product with the exact number of attributes values
            for product in products:
                if len(product.attribute_value_ids) == cont:
                    self.product_id = product.id
                    break
        if not self.product_id:
            product_tmpl = self.product_tmpl_id
            values = self.product_attribute_ids.mapped('value_id')
            if self._fields.get('partner_id'):
                # If our model has a partner_id field, language is got from it
                obj = self.env['product.attribute.value'].with_context(
                    lang=self.partner_id.lang)
                values = obj.browse(
                    self.product_attribute_ids.mapped('value_id').ids)
                obj = self.env['product.template'].with_context(
                    lang=self.partner_id.lang)
                product_tmpl = obj.browse(self.product_tmpl_id.id)
            self.name = self._get_product_description(
                product_tmpl, False, values)
        return {'domain': {'product_id': domain}}

    @api.model
    def _order_attributes(self, template, product_attribute_values):
        res = template._get_product_attributes_dict()
        res2 = []
        for val in res:
            value = product_attribute_values.filtered(
                lambda x: x.attribute_id.id == val['attribute_id'])
            if value:
                val['value_id'] = value
                res2.append(val)
        return res2

    @api.model
    def _get_product_description(self, template, product, product_attributes):
        name = product and product.name or template.name
        extended = self.user_has_groups(
            'product_variants_no_automatic_creation.'
            'group_product_variant_extended_description')
        if not product_attributes and product:
            product_attributes = product.attribute_value_ids
        values = self._order_attributes(template, product_attributes)
        if extended:
            description = "\n".join(
                "%s: %s" %
                (x['value_id'].attribute_id.name, x['value_id'].name)
                for x in values)
        else:
            description = ", ".join([x['value_id'].name for x in values])
        if not description:
            return name
        return ("%s\n%s" if extended else "%s (%s)") % (name, description)

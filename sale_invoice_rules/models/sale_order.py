# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Sobrecarga no neste metodo para inserir o rateio no price_unit
    @api.multi
    def invoice_line_create(self, invoice_id, qty, rateio=100):
        """
        Create an invoice line. The quantity to invoice can be positive 
        (invoice) or negative
        (refund).

        :param invoice_id: integer
        :param qty: float quantity to invoice
        """
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for line in self:
            if not float_is_zero(qty, precision_digits=precision):
                vals = line._prepare_invoice_line(qty=qty)
                vals['price_unit'] = vals['price_unit'] * rateio / 100
                vals.update({'invoice_id': invoice_id,
                             'sale_line_ids': [(6, 0, [line.id])]})
                self.env['account.invoice.line'].create(vals)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Separa itens em uma dict, keys são order.partner_invoice_id.id e value é 
    # dict de lista de recorrente/avulso/produto
    @api.multi
    def separate_invoice_types(self):

        order_lines_groups = {}
        for order in self:
            if order.state == 'draft':
                continue
            if order.partner_invoice_id.id not in order_lines_groups.keys():
                order_lines_groups.update(
                    {order.partner_invoice_id.id: {'recorrente': [], 'avulso': [], 'produto': []}})
            for line in order.order_line:
                if line.product_id.fiscal_type == 'product':
                    (order_lines_groups[order.partner_invoice_id.id]
                        ['produto'].append(line))
                else:
                    if line.recurring_line:
                        (order_lines_groups[order.partner_invoice_id.id]
                            ['recorrente'].append(line))
                    else:
                        (order_lines_groups[order.partner_invoice_id.id]
                            ['avulso'].append(line))
        return order_lines_groups

    def insert_invoice_lines(self, invoice, lines, rateio=100):
        for line in lines:
            qty = line.product_uom_qty
            line.invoice_line_create(invoice.id, qty, rateio)

    def create_invoices_rateio(self, order, invoice_lines, rateio=100, partner=0):

        inv_obj = self.env['account.invoice']
        inv_data = order._prepare_invoice()

        if partner:
            inv_data['account_id'] = partner.property_account_receivable_id.id
            inv_data['partner_id'] = partner.id
            inv_data['company_id'] = partner.company_invoice_id.id or inv_data['company_id']
            

        invoice = inv_obj.create(inv_data)

        self.insert_invoice_lines(invoice, invoice_lines, rateio)
        return invoice

    @api.multi
    def action_invoice_create_rateio(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, 
                    invoices are grouped by (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """

        invoice_lines = self.separate_invoice_types()

        # Lista que contem empresas que ja tiveram invoices criadas
        partner_ready = []

        # Lista de invoices
        invoices = []
        # Dicionario que tem a forma {invoice:[ordem1, ordem2, ...]}
        references = {}
        for order in self:
            if order.state == 'draft':
                continue
            # Caso o parceiro já tenha invoices criadas, irá procurar 
            # estas invoices e adicionar a ordem para invoices com 
            # mais de uma ordem de origem
            if order.partner_id in partner_ready:
                invs = [inv for inv in invoices if inv.partner_id.id ==
                        order.partner_invoice_id.id]
                for partner in order.partner_invoice_id.branch_ids:
                    for inv in invoices:
                        if inv.partner_id.id == partner.id:
                            invs.append(inv)
                for invoice in invs:
                    references[invoice].append(order)
                    # Impede que sejam adicionados ordens repetidas à lista 
                    # references
                    references[invoice] = list(set(references[invoice]))
            else:
                partner_ready.append(order.partner_id)
                rateio = 100

                # Cria fatura para os parceiros
                for partner in order.partner_invoice_id.branch_ids:

                    # Para recorrendo, rateio = %ND*%NF, para avulso rateio=%NF
                    inv = self.create_invoices_rateio(order, invoice_lines[order.partner_invoice_id.id]['recorrente'], partner.percentual_faturamento * (
                        100 - order.partner_id.percentual_nota_debito) / 100, partner)
                    invoices.append(inv)
                    references.update({inv: [order]})

                    inv = self.create_invoices_rateio(
                        order, invoice_lines[order.partner_invoice_id.id]['avulso'], partner.percentual_faturamento, partner)
                    invoices.append(inv)
                    references.update({inv: [order]})

                    rateio -= partner.percentual_faturamento

                # Cria faturas para a matriz
                inv = self.create_invoices_rateio(order, invoice_lines[order.partner_invoice_id.id]['recorrente'], rateio * (
                    100 - order.partner_id.percentual_nota_debito) / 100, order.partner_invoice_id)
                invoices.append(inv)
                references.update({inv: [order]})

                inv = self.create_invoices_rateio(
                    order, invoice_lines[order.partner_invoice_id.id]['avulso'], rateio, order.partner_invoice_id)
                invoices.append(inv)
                references.update({inv: [order]})

                # Cria fatura para produtos sem rateio
                inv = self.create_invoices_rateio(
                    order, invoice_lines[order.partner_invoice_id.id]['produto'])
                invoices.append(inv)
                references.update({inv: [order]})

                # Cria notas de debito
                # Seleciona o tipo de documento. Coloquei generico pra ver como funciona, ainda n sei o tipo de documento que sera colocado
                doc = self.env['br_account.fiscal.document'].search(
                    [('name', '=', 'Nota Fiscal Avulsa')])
                for partner in order.partner_invoice_id.branch_ids:

                    inv = self.create_invoices_rateio(order, invoice_lines[order.partner_invoice_id.id]['recorrente'], partner.percentual_faturamento * (
                        order.partner_id.percentual_nota_debito) / 100, partner)
                    inv.fiscal_document_id = doc
                    invoices.append(inv)
                    references.update({inv: [order]})

                inv = self.create_invoices_rateio(
                    order, invoice_lines[order.partner_invoice_id.id]['recorrente'], rateio * (order.partner_id.percentual_nota_debito) / 100)
                inv.fiscal_document_id = doc
                invoices.append(inv)
                references.update({inv: [order]})

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices:

            # Função para verificar invoices sem linhas e deletá-las
            if not invoice.invoice_line_ids:
                invoice.unlink()
                continue

            # Define o atributo origin da invoice
            origin = [order.name for order in references[invoice]]
            invoice.origin = ', '.join(origin)

            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity

            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)

            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()

            # invoice.message_post_with_view('mail.message_origin_link',
            #                                values={'self': invoice,
            #                                        'origin': references[invoice]},
            #                                subtype_id=self.env.ref('mail.mt_note').id)

        return [inv.id for inv in invoices]


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):

        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))

        orders = sale_orders.filtered(lambda x: len(
            x.partner_id.branch_ids) > 0)

        sale_orders = sale_orders.filtered(lambda x: len(
            x.partner_id.branch_ids) <= 0)

        if len(orders):
            orders.action_invoice_create_rateio()
        
        if len(sale_orders):
            self = self.with_context({'active_ids': sale_orders.ids})
            super(SaleAdvancePaymentInv, self).create_invoices()

        if self._context.get('open_invoices', False):
            return (orders | sale_orders).action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

        


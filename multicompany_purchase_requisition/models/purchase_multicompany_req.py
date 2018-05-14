from datetime import datetime
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

import time
import base64


class PurchaseMulticompanyReq(models.Model):
    _name = "purchase.multicompany.req"
    _order = "id desc"

    name = fields.Char(
        string='Agreement Reference', required=True, copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'purchase.multicompany.req'))
    ordering_date = fields.Date(string="Ordering Date")
    date_end = fields.Datetime(string='Agreement Deadline')
    schedule_date = fields.Date(string='Delivery Date', index=True)
    user_id = fields.Many2one(
        'res.users', string='Responsible', default=lambda self: self.env.user)
    description = fields.Text()
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'purchase.requisition'))
    line_ids = fields.One2many(
        'purchase.multicompany.req.line',
        'purchase_multicompany_req_id',
        string='Products to Purchase',
        states={'in_progress': [('readonly', False)]},
        copy=True)
    state = fields.Selection(
        [('in_progress', 'Confirmed'),
         ('in_negociation', 'In Negotiation'),
         ('done', 'Done'), ('cancel', 'Cancelled')],
        'Status', track_visibility='onchange', required=True,
        copy=False, default='in_progress')
    purchase_order_ids = fields.Many2many(
        'purchase.order', string="Purchase Orders",
        readonly=True,
    )
    purchase_requisition_ids = fields.Many2many(
        'purchase.requisition', string="Purchase Requisitions",
        readonly=True,
    )
    purchase_multicompany_ids = fields.Many2many(
        'purchase.multicompany', string="Purchase Multicompany",
        readonly=True,
    )

    @api.multi
    def assemble_selected(self, multicompany_requests):
        """ Famoso junta-tudo: junta todas as requisicoes e cria um único
        objeto com os produtos somados."""

        lines = self._assemble_selected_by_product(multicompany_requests)
        self._create_purchase_mult_req_lines(lines)

    def _assemble_selected_by_product(self, multicompany_requests):
        "Gera um dicionario com todos os produtos, somando suas quantidades."

        lines = {}
        for request in multicompany_requests:
            for line in request.line_ids:
                total_qty = line.product_qty + line.qty_increment
                if line.product_id in lines:
                    lines[line.product_id][0] += total_qty
                    lines[line.product_id][1].append(line.id)
                else:
                    lines[line.product_id] = [total_qty, [line.id]]
        return lines

    def _create_purchase_mult_req_lines(self, lines):
        for line in lines.items():
            vals = {
                'product_id': line[0].id,
                'product_uom_id': line[0].uom_id.id,
                'product_qty': line[1][0],
                'qty_increment': 0,
                'requisition_line_ids': [(6, 0, line[1][1])],
                'purchase_multicompany_req_id': self.id,
            }
            self.env['purchase.multicompany.req.line'].create(vals)

    def action_in_negociation(self):
        """Separa as linhas de acordo com o campo 'purchase_requisition'
        e fornecedor"""

        if not all(obj.line_ids for obj in self):
            raise UserError(
                _('You cannot confirm call because there is no product line.'))
        for line in self.purchase_multicompany_ids:
            # Muda o status da linha para 'em negociação', bloqueando mudanças
            # nas mesmas
            line.action_negociation()
        rfq = {}
        tenders = {}
        for line in self.line_ids:
            if not line.product_id.seller_ids:
                raise UserError(_('You cannot confirm because the product %s \
does not have a supplier' % (line.product_id.name)))
            seller_id = line.product_id.seller_ids[0].name.id
            product_id = line.product_id
            total_qty = line.product_qty + line.qty_increment
            if line.product_id.purchase_requisition == 'rfq':

                if seller_id not in rfq:
                    rfq[seller_id] = {}

                rfq[seller_id][line.id] = [product_id, total_qty]

            elif line.product_id.purchase_requisition == 'tenders':

                if seller_id not in tenders:
                    tenders[seller_id] = {}

                tenders[seller_id][line.id] = [product_id, total_qty]

        self._create_purchase_orders(rfq)
        self._create_purchase_requisition(tenders)
        self.write({
            'state': 'in_negociation', 'ordering_date': datetime.now()})

    def _create_purchase_requisition(self, tender_dict):
        "Cria purchase_requisitions de acordo com os dados fornecidos"

        pr_lines = []
        requisition_ids = {}
        req_ids = []

        for vendor_id, lines in tender_dict.items():
            for req_line, product_data in lines.items():
                line_vals = {
                    'product_id': product_data[0].id,
                    'product_qty': product_data[1],
                    'price_unit': product_data[0].seller_ids[0].price,
                }
                pr_lines.append(self.env[
                    'purchase.requisition.line'].create(line_vals).id)
            vals = {
                'vendor_id': vendor_id,
                'line_ids': [(6, 0, pr_lines)],
                'user_id': self[0].user_id.id,
                'centralizador_id': self.id,
            }

            req_id = self.env['purchase.requisition'].create(vals).id
            requisition_ids[vendor_id] = req_id
            req_ids.append(req_id)
        self.write({'purchase_requisition_ids': [(6, 0, req_ids)]})
        self._create_purchase_orders(tender_dict, requisition_ids)

    def _create_purchase_orders(self, rfq_dict, req_ids=False):
        "Cria purchase orders de acordo com as informações fornecidas"

        for vendor_id, lines in rfq_dict.items():
            vals = {
                'partner_id': vendor_id,
                'requisition_id': req_ids[vendor_id] if req_ids else None,
                'centralizador_id': self.id,
            }
            po_id = self.env['purchase.order'].create(vals)

            for req_line_id, product_data in lines.items():
                line_vals = {
                    'product_id': product_data[0].id,
                    'name': product_data[0].name,
                    'date_planned': datetime.now(),
                    'product_uom': product_data[0].uom_id.id,
                    'product_qty': product_data[1],
                    'prod_original_qty': product_data[1],
                    'price_unit': product_data[0].seller_ids[0].price,
                    'order_id': po_id.id,
                    'req_line_id': req_line_id,
                }
                po_line_id = self.env['purchase.order.line'].create(line_vals)

                self.env['purchase.multicompany.req.line'].browse(
                    req_line_id).write({'po_line_id': po_line_id.id})

            self.write({'purchase_order_ids': [(4, po_id.id, 0)]})

    @api.multi
    def action_cancel(self):
        """Muda o status para cancelado e remove o link entre as
        purchase_orders e purchase_requisition_ids, e também coloca o status
        das orders/requisitions para cancelado"""

        for item in self.purchase_order_ids:
            item.write({'state': 'cancel'})
        for item in self.purchase_requisition_ids:
            item.write({'state': 'cancel'})

        self.write({'purchase_order_ids': [(5, 0, 0)]})
        self.write({'purchase_requisition_ids': [(5, 0, 0)]})
        self.write({'state': 'cancel'})

    @api.multi
    def action_progress(self):
        # Pretty straight forward, dont you think?
        self.write({'state': 'in_progress'})

    @api.multi
    def action_done(self):
        """Verifica se todos os purchase_orders estão em 'done' e logo em seguida
        distribui os eventuais incrementos de quantidade para todos pedidos de
        requisicao iniciais"""

        if not all(item.state in ('purchase', 'done') for item in
                   self.purchase_order_ids):
            raise UserError(_(
                u"There is Purchase Orders which are not in 'purchase' or 'done' state. \
Please finish the PO process before changing this object's state."
            ))
        for po_id in self.purchase_order_ids:
            for line in po_id.order_line:
                pmr_line = self.env['purchase.multicompany.req.line'].search([
                    ('product_id', '=', line.product_id.id),
                    ('purchase_multicompany_req_id', '=', self.id)])
                pmr_line.write({'qty_increment': line.qty_increment})
                pmr_line._qty_increment_distribution()
        self.write({'state': 'done'})

    @api.multi
    def _send_email_romaneio(self):

        mail = self.env['mail.template'].search([
            ('model_id', '=', 'purchase.order')])[0]
        if not mail:
            raise UserError('Modelo de email padrão não configurado')

        for po in self.purchase_order_ids:
            romaneio_report = self.env['ir.actions.report'].search(
                [('report_name', '=',
                    'multicompany_purchase_requisition.report_romaneio')])
            report_service = romaneio_report.xml_id
            romaneio, dummy = self.env.ref(
                report_service).render_qweb_pdf([po.id])
            report_name = safe_eval(romaneio_report.print_report_name,
                                    {'object': po, 'time': time})
            filename = "%s.%s" % (report_name, "pdf")

            attachment_id = po.env['ir.attachment'].create({
                'name': filename,
                'datas': base64.b64encode(romaneio),
                'datas_fname': filename,
                'mimetype': 'application/pdf',
                'res_model': 'purchase.order',
                'res_id': po.id,
            })

            values = {
                "attachment_ids": [attachment_id.id]
            }

            mail.send_mail(po.id, email_values=values)

    class PurchaseMulticompanyReqLine(models.Model):
        _name = "purchase.multicompany.req.line"
        _description = "Purchase Multicompany Requisition Line"
        _rec_name = 'product_id'

        product_id = fields.Many2one(
            'product.product', string='Product',
            domain=[('purchase_ok', '=', True)], required=True)
        product_uom_id = fields.Many2one(
            'product.uom', string='Product Unit of Measure')
        product_qty = fields.Float(
            string='Quantity', digits=dp.get_precision(
                'Product Unit of Measure'))
        qty_increment = fields.Float(
            string='Increment', digits=dp.get_precision(
                'Product Unit of Measure'))

        company_id = fields.Many2one(
            'res.company',
            string='Company',
            store=True, readonly=True,
            default=lambda self: self.env['res.company']._company_default_get(
                'purchase.multicompany.line'))

        purchase_multicompany_req_id = fields.Many2one(
            'purchase.multicompany.req',
            string="Purchase Multicompany Requisition")
        requisition_line_ids = fields.Many2many(
            'purchase.multicompany.line', string='Purchase Company',
            ondelete='cascade')
        po_line_id = fields.Many2one('purchase.order.line')

        state = fields.Selection(
            related="purchase_multicompany_req_id.state")

        @api.onchange('product_id')
        def _onchange_product_id(self):
            if self.product_id:
                self.product_uom_id = self.product_id.uom_id
                self.product_qty = 1.0

        def _qty_increment_distribution(self):
            "Distribui qty_increment para todas as requisicoes"

            if self.qty_increment:
                total_increment = self.qty_increment
                num_req_lines = len(self.requisition_line_ids)
                for line in self.requisition_line_ids:
                    increment = round(total_increment / num_req_lines)
                    line.qty_increment = increment
                    total_increment -= increment
                    num_req_lines -= 1

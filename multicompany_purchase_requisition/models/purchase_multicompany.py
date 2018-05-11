# © 2018 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class PurchaseMulticompany(models.Model):
    _name = "purchase.multicompany"
    _description = "Purchase Requisition for Multi Company"
    _inherit = ['mail.thread']
    _order = "id desc"

    name = fields.Char(
        string='Agreement Reference', required=True, copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'purchase.multicompany.requisition'))
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
        'purchase.multicompany.line', 'requisition_id',
        string='Products to Purchase', states={'done': [('readonly', True)]},
        copy=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'Confirmed'),
         ('in_negociation', 'In Negotiation'),
         ('done', 'Done'), ('cancel', 'Cancelled')],
        'Status', track_visibility='onchange', required=True,
        copy=False, default='draft')
    centralizador_id = fields.Many2one(
        'purchase.multicompany.req',
        string="Centralizador", readonly=True,
    )

    @api.multi
    def action_cancel(self):
        if self.centralizador_id and \
                self.centralizador_id.state not in ['cancel']:
            raise UserError(
                _(u'You cannot cancel this call because it is linked \
to a non cancelled Assembled Multicompany Purchase object (%s).\
Try cancelling the Assembled Multicompany Purchase object first.')
                % (self.centralizador_id.name))
        else:
            self.write({'state': 'cancel'})

    @api.multi
    def action_in_progress(self):
        if not all(obj.line_ids for obj in self):
            raise UserError(
                _(u'You cannot confirm call because there is no product line.'
                  ))
        self.write({'state': 'in_progress', 'ordering_date': datetime.now()})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})

    @api.multi
    def action_negociation(self):
        self.write({'state': 'in_negociation'})

    @api.multi
    def assemble_selected(self):

        if not all(item.state == 'in_progress' for item in self):
            raise UserError(
                _(u"It's not possible to assemble purchase requisitions \
which are not in 'confirmed' state. Please, verify the purchase's state \
and try again later."
                  ))

        vals = {
            'name': 'PMR %s' % (self.ids),
            'description': 'Created from purchase.multicompany ID: %s'
            % (self.ids),
            'state': 'in_progress',
            'purchase_multicompany_ids': [(6, 0, self.ids)],
        }
        centralizador_id = self.env[
            'purchase.multicompany.req'].create(vals)

        for item in self:
            item.centralizador_id = centralizador_id.id
        centralizador_id.assemble_selected(list(self))


class PurchaseMulticompanyLine(models.Model):
    _name = "purchase.multicompany.line"
    _description = "Purchase MultiCompany Line"
    _rec_name = 'product_id'

    product_id = fields.Many2one(
        'product.product', string='Product',
        domain=[('purchase_ok', '=', True)], required=True)
    product_uom_id = fields.Many2one(
        'product.uom', string='Product Unit of Measure')
    product_qty = fields.Float(
        string='Quantity', digits=dp.get_precision('Product Unit of Measure'))
    qty_increment = fields.Float(
        string='Increment', digits=dp.get_precision('Product Unit of Measure'))
    requisition_id = fields.Many2one(
        'purchase.multicompany', string='Purchase Company', ondelete='cascade')
    company_id = fields.Many2one(
        'res.company', related='requisition_id.company_id', string='Company',
        store=True, readonly=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'purchase.multicompany.line'))

    pm_req_line_id = fields.Many2one('purchase.multicompany.req.line')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
            self.product_qty = 1.0

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AdditionalInfoWizard(models.TransientModel):
    _name = 'additional.info.wizard'

    additional_info = fields.Text('Additional Info')

    state = fields.Selection([('done', 'Additional Info')])

    @api.multi
    def action_confirm(self):
        so_id = self.env.context.get('active_id')

        if not so_id:
            raise UserError(_(u'Sale order ID not found in context'))

        # Getting the last line from SO
        sale_order_line = self.env['sale.order.line'].search([
            ('order_id', '=', so_id)], order="id desc", limit=1)

        if sale_order_line:
            sale_order_line.write(
                {'additional_info': self.additional_info})

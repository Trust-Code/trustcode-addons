# © 2020 Danimar Ribeiro, Trustcode
# Part of Trustcode. See LICENSE file for full copyright and licensing details.

from odoo import models



class SaleOrder(models.Model):
    _inherit = "sale.order"

    # def action_cancel(self):
    #     # res = super(SaleOrder, self).action_cancel()
    #     # for order in self:
    #     #     for transaction_id in order.transaction_ids:
    #     #         if (
    #     #             transaction_id
    #     #             and transaction_id.acquirer_id.provider == "zoop"
    #     #         ):
    #     #             iugu.config(token=transaction_id.acquirer_id.iugu_api_key)
    #     #             invoice_api = iugu.Invoice()
    #     #             invoice_api.cancel(transaction_id.acquirer_reference)

    #     # return res

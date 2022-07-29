from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    kk_site_id = fields.Many2one("kk.sites", string="Site")
    kk_site_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente Site",
        related="kk_site_id.partner_id",
    )


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(
            line
        )
        res.update({"kk_site_id": line.kk_site_id})
        return res

    @api.multi
    def action_invoice_open(self):
        for item in self:
            if item.type == "in_invoice":
                if not item.reference:
                    raise UserError(
                        "Favor preencher o campo 'Referência do Fornecedor'"
                    )
                if not all(
                    line.purchase_line_id.kk_delivery_date
                    for line in item.invoice_line_ids
                ):
                    raise UserError(
                        "Favor solicitar que o responsável preencha o campo Data de Entrega no Pedido de Compra!"
                    )
        return super(AccountInvoice, self).action_invoice_open()

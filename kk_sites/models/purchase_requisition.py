from odoo import models, fields, api


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    kk_site_id = fields.Many2one("kk.sites", string="Site")
    kk_site_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente Site",
        related="kk_site_id.partner_id",
    )
    kk_site_city_state = fields.Char(
        string="Cidade/UF", compute="_compute_kk_site_city_state"
    )

    @api.multi
    @api.onchange("kk_site_id")
    def _compute_kk_site_city_state(self):
        for item in self:
            item.kk_site_city_state = (
                "{}/{}".format(
                    item.kk_site_id.city_id.name,
                    item.kk_site_id.state_id.code,
                )
                if item.kk_site_id
                else ""
            )

    @api.multi
    def _prepare_purchase_order_line(
        self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False
    ):
        self.ensure_one()
        res = super(
            PurchaseRequisitionLine, self
        )._prepare_purchase_order_line(
            name, product_qty, price_unit, taxes_ids
        )
        res.update({"kk_site_id": self.kk_site_id.id})
        return res

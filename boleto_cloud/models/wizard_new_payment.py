from odoo import api, fields, models


class WizardNewPaymentInvoice(models.TransientModel):
    _inherit = 'wizard.new.payment.invoice' 

    def action_generate_new_payment(self):
        super(WizardNewPaymentInvoice, self).action_generate_new_payment()
        self.move_id.generate_boleto_cloud_transactions()
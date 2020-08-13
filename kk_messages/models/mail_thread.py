from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'
    
    @api.multi
    def _message_auto_subscribe_notify(self, partner_ids):
        """ Notify newly subscribed followers of the last posted message.
            :param partner_ids : the list of partner to add as needaction partner of the last message
                                 (This excludes the current partner)
        """
        print(self.env.context)
        print(self)
        if not partner_ids:
            return

        if self.env.context.get('mail_auto_subscribe_no_notify'):
            return

        # send the email only to the current record and not all the ids matching active_domain !
        # by default, send_mail for mass_mail use the active_domain instead of active_ids.
        if 'active_domain' in self.env.context:
            ctx = dict(self.env.context)
            ctx.pop('active_domain')
            self = self.with_context(ctx)

        for record in self:
            
            template_name = 'mail.message_user_assigned'
            vals = {}
            subject = None
            if self._name == 'account.invoice':
                template_name = 'kk_messages.message_invoice_created'
                vals['subject'] = 'Fatura criada'
            
            record.message_post_with_view(
                template_name,
                composition_mode='mass_mail',
                partner_ids=[(4, pid) for pid in partner_ids],
                auto_delete=True,
                auto_delete_message=True,
                parent_id=False, # override accidental context defaults
                subtype_id=self.env.ref('mail.mt_note').id, **vals)
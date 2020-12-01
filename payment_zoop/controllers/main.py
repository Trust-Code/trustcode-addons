import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class PagHiperController(WebsiteSale):

    @http.route(
        '/zoop/notificacao/', type='http', auth="none",
        methods=['GET', 'POST'], csrf=False)
    def zoop_form_feedback(self, **post):
        _logger.info(post)
        request.env['payment.transaction'].sudo().form_feedback(post, 'zoop')
        return "<status>OK</status>"

    @http.route(
        '/zoop/checkout/redirect', type='http',
        auth='public', methods=['GET', 'POST'], website=True, sitemap=False)
    def zoop_checkout_redirect(self, **post):
        if 'secure_url' in post:
            order = request.website.sale_get_order()
            order.action_confirm()
            order.transaction_ids[0].write({
                'state': 'pending',
                'transaction_url': post.get('secure_url')
            })
            return request.redirect('/shop/payment/validate')
        else:
            raise UserError('Erro ao gerar boleto com o Zoop.\n' +
                            'Por favor, tente mais tarde.')

    @http.route(['/shop/confirmation'], type='http',
                auth="public", website=True, sitemap=False)
    def payment_confirmation(self, **post):
        res = super(PagHiperController, self).payment_confirmation(**post)

        sale_order_id = request.session.get('sale_last_order_id')

        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            tx = order.get_portal_last_transaction()

            if tx.transaction_url:
                return request.render("payment_zoop.zoop_confirmation", {'order': order})

        return res

import logging
from odoo import http
from odoo.http import request
from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)


class PagHiperController(http.Controller):

    @http.route(
        '/zoop/notificacao/', type='http', auth="none",
        methods=['GET', 'POST'], csrf=False)
    def zoop_form_feedback(self, **post):
        request.env['payment.transaction'].sudo().form_feedback(post, 'zoop')
        return "<status>OK</status>"

    @http.route(
        '/zoop/checkout/redirect', type='http',
        auth='none', methods=['GET', 'POST'])
    def zoop_checkout_redirect(self, **post):
        post = post
        if 'secure_url' in post:
            return redirect(post['secure_url'])

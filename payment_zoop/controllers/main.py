import logging
from odoo import http
from odoo.http import request
from werkzeug.utils import redirect
import webbrowser

_logger = logging.getLogger(__name__)


class PagHiperController(http.Controller):

    @http.route(
        '/zoop/notificacao/', type='http', auth="none",
        methods=['GET', 'POST'], csrf=False)
    def zoop_form_feedback(self, **post):
        _logger.info(post)
        request.env['payment.transaction'].sudo().form_feedback(post, 'zoop')
        return "<status>OK</status>"

    @http.route(
        '/zoop/checkout/redirect', type='http',
        auth='none', methods=['GET', 'POST'])
    def zoop_checkout_redirect(self, **post):
        if 'secure_url' in post:
            webbrowser.open_new_tab(post['secure_url'])
            return redirect('/')
            # return redirect(post['secure_url'])

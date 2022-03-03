import json
from odoo import http, SUPERUSER_ID
from odoo.http import request


class WordpressController(http.Controller):

    @http.route(['/wordpress/form'], auth='public', cors='*', csrf=False)
    def trustcode_my_document_like(self, **kwargs):
        if request.httprequest.headers.get("Token") == "ABC123DEF456":
            partner = request.env["res.partner"].with_user(SUPERUSER_ID).search(
                [("email", "=", kwargs.get("email_address"))])
            if not partner:
                partner = request.env["res.partner"].with_user(SUPERUSER_ID).create({
                    "name": kwargs.get("first_name") + " " + kwargs.get("last_name"),
                    "email": kwargs.get("email_address"),
                    "phone": kwargs.get("phone_number"),
                    "company_type": "person",
                })

            lead = request.env["crm.lead"].with_user(SUPERUSER_ID).create({
                "name": kwargs.get("subject"),
                "contact_name": kwargs.get("first_name") + " " + kwargs.get("last_name"),
                "email_from": kwargs.get("email_address"),
                "phone": kwargs.get("phone_number"),
                "description": kwargs.get("message"),
                "partner_id": partner.id,
                "type": "opportunity",
                "team_id": 2,
            })
            lead.message_post(body=json.dumps(kwargs))
        return "OK"
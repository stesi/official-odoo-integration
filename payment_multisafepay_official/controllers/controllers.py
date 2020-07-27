# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.http import Response
import werkzeug
import json
import logging

_logger = logging.getLogger(__name__)


class MultiSafepayController(http.Controller):
    @http.route(
        ['/payment/multisafepay/notification'],
        type='http',
        auth='none',
    )
    def notification_payment(self, **post):
        request.env['payment.transaction'].sudo().form_feedback(post, 'multisafepay')
        return werkzeug.utils.redirect('/payment/process')

    @http.route(
        ['/payment/multisafepay/init'],
        type='http',
        auth='none',
        methods=['POST'],
        csrf=False,
    )
    def init_payment(self, **post):
        acquirer = request.env['payment.acquirer'].search([('id', '=', post['acquirer'])], limit=1)

        try:
            multisafepay_client = acquirer.get_multisafepay_client()
        except ValueError as exception:
            return Response(str(exception), status=400)

        post['ip_address'] = request.httprequest.environ.get('REMOTE_ADDR')
        post['user_agent'] = request.httprequest.environ.get('HTTP_USER_AGENT', '')
        post['sale_order_id'] = request.session.get('sale_last_order_id')

        order_body = acquirer.build_order_body(post)
        _logger.info(json.dumps(order_body))
        order_response = multisafepay_client.order.create(order_body)

        if order_response.get('success', False):
            payment_url = order_response.get('data').get('payment_url')
            return werkzeug.utils.redirect(payment_url)

        return Response('MultiSafepay error message: ' + order_response.get('error_info', 'unknown'), status=400)

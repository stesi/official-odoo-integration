from odoo import models, fields, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
import logging
import pprint
from datetime import datetime

_logger = logging.getLogger(__name__)


class MultiSafepayPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    multisafepay_order_id = fields.Char(string='Order ID in MultiSafepay')

    def _multisafepay_form_get_tx_from_data(self, data):
        multisafepay_order_id = data.get('transactionid')
        if multisafepay_order_id is None:
            raise ValidationError('Invalid transaction id')

        reference = multisafepay_order_id.split('_')[0]
        tx = self.search([('reference', '=', reference)])

        if not tx or len(tx) > 1:
            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return tx

    def _multisafepay_form_get_invalid_parameters(self, data):
        return []

    def _multisafepay_form_validate(self, data):
        multisafepay_client = self.acquirer_id.get_multisafepay_client()
        order = multisafepay_client.order.get(data.get('transactionid'))

        if self.handle_refund_transactions(order):
            return

        if self.state == 'done':
            return True

        if not order.get('success', False):
            error_message = order.get('error_info', 'Request failed')
            self._set_transaction_error(error_message)
            return True

        if not order.get('data').get('order_id'):
            self._set_transaction_cancel()
            return True

        order_status = order.get('data').get('status', False)
        self.write({
            'acquirer_reference': order.get('data').get('transaction_id', 'undefined'),
            'multisafepay_order_id': order.get('data').get('order_id', 'undefined'),
        })

        if order_status in ['void', 'declined', ] and data.get('type') == 'cancel':
            self._set_transaction_cancel()
            return True

        if order_status in ['completed', 'shipped']:
            self._set_transaction_done()
            return True

        if order_status in ['initialized', 'uncleared', ]:
            self._set_transaction_pending()
            return True

        self._set_transaction_error('Transaction status: ' + order_status)
        return True

    def update_order(self):
        if not self.invoice_ids:
            return

        multisafepay_client = self.acquirer_id.get_multisafepay_client()
        multisafepay_client.order.update(self.multisafepay_order_id, {
            'invoice_id': self.invoice_ids[0].id
        })

    def handle_refund_transactions(self, order):
        if order.get('data', {}).get('payment_details', {}).get('type', '') in ['PAYPAL', 'AFTERPAY']:
            costs = order.get('data').get('costs', [])
            if not costs or order.get('data').get('status', False) != 'completed':
                return False
            for cost in costs:
                if cost.get('status', 'void') == 'void':
                    continue
                invoice = self.env['account.move'].sudo().search(
                        [('multisafepay_refund_id', '=', cost.get('transaction_id'))], limit=1)
                if not invoice:
                    continue
                invoice.set_refund_paid()
            return True
        else:
            related_transactions = order.get('data').get('related_transactions', [])
            if not related_transactions:
                return False
            for related_tx in related_transactions:
                if related_tx.get('status', False) == 'completed':
                    invoice = self.env['account.move'].sudo().search(
                        [('multisafepay_refund_id', '=', related_tx.get('transaction_id'))], limit=1)
                    if not invoice:
                        continue
                    invoice.set_refund_paid()
            return True


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def send_to_shipper(self):
        super(StockPicking, self).send_to_shipper()

        order = self.env['sale.order'].sudo().search([('name', 'ilike', self.origin)], limit=1)
        multisafepay_transactions = list(filter(lambda tx: tx.provider == 'multisafepay', order.transaction_ids))
        if not multisafepay_transactions:
            return

        multisafepay_client = multisafepay_transactions[0].acquirer_id.get_multisafepay_client()
        for multisafepay_tx in multisafepay_transactions:
            multisafepay_client.order.update(multisafepay_tx.multisafepay_order_id, {
                "status": "shipped",
                "tracktrace_code": self.carrier_tracking_ref,
                "tracktrace_url": self.carrier_tracking_url,
                "ship_date": datetime.now().strftime("%d-%m-%Y"),
                "carrier": self.carrier_id.name,
            })

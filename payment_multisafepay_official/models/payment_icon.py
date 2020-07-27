from odoo import models, fields
from odoo import modules
import base64

IDEAL_PAYMENT_METHOD = 'IDEAL'
SOFORT_PAYMENT_METHOD = 'DIRECTBANK'
PAYPAL_PAYMENT_METHOD = 'PAYPAL'
BELFIUS_PAYMENT_METHOD = 'BELFIUS'
ING_HOME_PAYMENT_METHOD = 'INGHOME'
KBC_PAYMENT_METHOD = 'KBC'
ALIPAY_PAYMENT_METHOD = 'ALIPAY'
BETAAPLAN_PAYMENT_METHOD = 'SANTANDER'
DBRTP_PAYMENT_METHOD = 'DBRTP'
AFTERPAY_PAYMENT_METHOD = 'AFTERPAY'
PAY_AFTER_DELIVERY_PAYMENT_METHOD = 'PAYAFTER'
E_INVOICING_PAYMENT_METHOD = 'EINVOICE'
MAESTRO_PAYMENT_METHOD = 'MAESTRO'
EPS_PAYMENT_METHOD = 'EPS'
GIROPAY_PAYMENT_METHOD = 'GIROPAY'
JCB_PAYMENT_METHOD = 'JCB'
BANKTRANS_PAYMENT_METHOD = 'BANKTRANS'
APPLEPAY_PAYMENT_METHOD = 'APPLEPAY'
BANCONTACT_PAYMENT_METHOD = 'MISTERCASH'
TRUSTLY_PAYMENT_METHOD = 'TRUSTLY'
PAY_IN_ADVANCE_PAYMENT_METHOD = 'PAYINADV'
KLARNA_PAYMENT_METHOD = 'KLARNA'
DIRECT_DEBIT_PAYMENT_METHOD = 'DIRDEB'
MASTERCARD_PAYMENT_METHOD = 'MASTERCARD'
VISA_PAYMENT_METHOD = 'VISA'
AMEX_PAYMENT_METHOD = 'AMEX'
MULTISAFEPAY_PAYMENT_METHOD = 'MultiSafepay'
DOTPAY_PAYMENT_METHOD = 'DOTPAY'
IDEAL_QR_PAYMENT_METHOD = 'IDEALQR'
MCACQ_MS_PAYMENT_METHOD = 'MCACQMS'

DEFAULT_VALUES = {
    KLARNA_PAYMENT_METHOD: {
        'countries': ('NL', 'AT', 'DE',),
        'convert_to_eur': True,
        'direct_supported': False,
    },
    AFTERPAY_PAYMENT_METHOD: {
        'countries': ('NL', 'BE',),
        'convert_to_eur': True,
        'direct_supported': True,
    },
    # gb
    BANKTRANS_PAYMENT_METHOD: {
        'countries': ('AT', 'BE', 'CZ', 'FR', 'DE',  'HU', 'IT', 'NL', 'PL', 'PT', 'ES', ),
        'convert_to_eur': True,
    },
    DBRTP_PAYMENT_METHOD: {
        'countries': ('AT', 'BE', 'FI', 'DE', 'IT', 'NL', 'ES', ),
        'convert_to_eur': True,
        'min_amount': 1,
        'max_amount': 15000,
        'direct_supported': True,
    },
    BETAAPLAN_PAYMENT_METHOD: {
        'countries': ('NL',),
        'convert_to_eur': True,
        'min_amount': 250,
        'max_amount': 8000,
        'direct_supported': True,
    },
    E_INVOICING_PAYMENT_METHOD: {
        'countries': ('NL',),
        'convert_to_eur': True,
        'min_amount': 200,
        'max_amount': 300,
    },
    PAY_AFTER_DELIVERY_PAYMENT_METHOD: {
        'countries': ('NL',),
        'convert_to_eur': True,
        'max_amount': 300,
    },
    MAESTRO_PAYMENT_METHOD: {
        'convert_to_eur': True,
    },
    EPS_PAYMENT_METHOD: {
        'convert_to_eur': True,
    },
    GIROPAY_PAYMENT_METHOD: {
        'convert_to_eur': True,
    },
    JCB_PAYMENT_METHOD: {
        'convert_to_eur': True,
    },
    APPLEPAY_PAYMENT_METHOD: {
        'convert_to_eur': True,
    },
    BANCONTACT_PAYMENT_METHOD: {
        'countries': ('BE',),
        'convert_to_eur': True,
    },
    # gb
    TRUSTLY_PAYMENT_METHOD: {
        'countries': ('AT', 'BE', 'BG', 'HR', 'CY', 'GR', 'CZ', 'DK', 'EE', 'FI', 'DE', 'HU',
                      'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI',
                      'ES', 'SE', ),
        'convert_to_eur': True,
    },
    PAY_IN_ADVANCE_PAYMENT_METHOD: {
        'convert_to_eur': True,
    },
    DIRECT_DEBIT_PAYMENT_METHOD: {
        'convert_to_eur': True,
    },
    VISA_PAYMENT_METHOD: {
        'is_credit_card': True,
    },
    MASTERCARD_PAYMENT_METHOD: {
        'is_credit_card': True,
    },
    AMEX_PAYMENT_METHOD: {
        'is_credit_card': True,
    },
    SOFORT_PAYMENT_METHOD: {
        'countries': ('AT', 'BE', 'DE', 'IT', 'ES', 'CH', 'PL',),
        'convert_to_eur': True,
    },
    IDEAL_QR_PAYMENT_METHOD: {
        'direct_supported': True,
    },
    IDEAL_PAYMENT_METHOD: {
        'direct_supported': True,
    },
    PAYPAL_PAYMENT_METHOD: {
        'direct_supported': True,
    },
    BELFIUS_PAYMENT_METHOD: {
        'direct_supported': True,
    },
    ING_HOME_PAYMENT_METHOD: {
        'direct_supported': True,
    },
    KBC_PAYMENT_METHOD: {
        'direct_supported': True,
    },
    ALIPAY_PAYMENT_METHOD: {
        'direct_supported': True,
    },
}


class MultiSafepayPaymentIcon(models.Model):
    _inherit = 'payment.icon'

    enabled = fields.Boolean(string='Enabled', default=True)
    title = fields.Char(string='Title')
    min_amount = fields.Integer(string='Min order amount (EUR)', default=1)
    max_amount = fields.Integer(string='Max order amount (EUR)', default=100000)
    provider = fields.Char(string='Provider')
    currency_ids = fields.Many2many('res.currency', string='Currency')
    country_ids = fields.Many2many('res.country', string='Country')
    customer_group = fields.Selection([
        ('all', 'All users'),
        ('logged-in', 'Logged in users'),
        ('non-logged-in', 'Non logged in users'),
    ], string='Customer group', default='all')
    is_credit_card = fields.Boolean(string='Is credit card', default=False)

    editable_min_amount = fields.Boolean(string='Can be min amount be edit', default=True)
    editable_max_amount = fields.Boolean(string='Can be max amount be edit', default=True)
    editable_country = fields.Boolean(string='Can be country be edit', default=True)

    @staticmethod
    def create_multisafepay_icon(payment_method_id, env, provider):
        if not payment_method_id:
            return
        path = modules.get_module_resource(
            'payment_multisafepay_official',
            'static/src/img/payment_methods',
            payment_method_id + '.png'
        )
        if not path:
            path = modules.get_module_resource(
                'payment_multisafepay_official',
                'static/src/img/payment_methods',
                'MultiSafepay.png'
            )

        with open(path, 'rb') as file:
            image = base64.b64encode(file.read())

        payment_icon_deafult_value = DEFAULT_VALUES.get(payment_method_id, {})
        country_codes = payment_icon_deafult_value.get('countries', ())
        countries = [env.ref('base.' + country.lower()).id for country in country_codes]

        min_amount = 1
        if payment_icon_deafult_value.get('min_amount', False):
            min_amount = payment_icon_deafult_value.get('min_amount')

        max_amount = 100000
        if payment_icon_deafult_value.get('max_amount', False):
            max_amount = payment_icon_deafult_value.get('max_amount')

        payment_icon = env['payment.icon'].create(vals_list={
            'name': payment_method_id,
            'title': payment_method_id.upper(),
            'provider': provider,
            'is_credit_card': payment_icon_deafult_value.get('is_credit_card', False),
            'image': image,
            'country_ids': countries,
            'min_amount': min_amount,
            'max_amount': max_amount,
            'editable_country': False if countries else True,
            'editable_min_amount': False if payment_icon_deafult_value.get('min_amount', False) else True,
            'editable_max_amount': False if payment_icon_deafult_value.get('max_amount', False) else True,
        })

        return payment_icon

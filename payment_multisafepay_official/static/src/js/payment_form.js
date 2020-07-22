odoo.define('payment_multisafepay_official.payment_form', function (require) {
"use strict";

    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var rpc = require("web.rpc");

    var _t = core._t;
    var PaymentForm = require('payment.payment_form');

    PaymentForm.include({
        events: {
            'submit': 'onSubmit',
            'click #o_payment_form_pay': 'payEvent',
            'click #o_payment_form_add_pm': 'addPmEvent',
            'click button[name="delete_pm"]': 'deletePmEvent',
            'click .o_payment_form_pay_icon_more': 'onClickMorePaymentIcon',
            'click .o_payment_acquirer_select': 'radioClickEvent',
            'click input[name="pm_id"]': 'radioClickEvent',
            'change input[name="multisafepay_pm_id"]': 'changeMultiSafepayAcquirerStatus',
            'change select[name="cc_multisafepay_pm_id"]': 'changeCreditCardMethod',
            'change select[name="ideal_issuer_id"]': 'changeIdealIssuer',
        },

        changeIdealIssuer: function () {
            var select = this.$('select[name="ideal_issuer_id"]');
            var input = this.$('input[data-ideal-issuer="true"]')[0];
            input.setAttribute('data-issuer-id', select.val());
        },

        changeCreditCardMethod: function () {
            var select = this.$('select[name="cc_multisafepay_pm_id"]');
            var input = this.$('input[data-credit-card="true"]')[0];
            input.setAttribute('data-payment-method-id', select.val());
            input.setAttribute('data-multisafepay-aq', select.val());
            input.setAttribute('value', 'form_' + select.val());
        },

        changeMultiSafepayAcquirerStatus: function () {
            var checked_radio = this.$('input[name="multisafepay_pm_id"]:checked');
            if (checked_radio.length !== 1) {
                return;
            }
            var ideal_select = this.$('select[name="ideal_issuer_id"]')[0];
            var cc_select = this.$('select[name="cc_multisafepay_pm_id"]')[0];

            if (checked_radio[0].getAttribute('data-ideal-issuer') == 'true') {
                cc_select.setAttribute('hidden', '');
                ideal_select.removeAttribute('hidden');
            } else if (checked_radio[0].getAttribute('data-credit-card') == 'true') {
                ideal_select.setAttribute('hidden', '');
                cc_select.removeAttribute('hidden');
            } else {
                cc_select.setAttribute('hidden', '');
                ideal_select.setAttribute('hidden', '');
            }

            $('input[data-provider="multisafepay"]').prop("checked", true);
        },

        updateNewPaymentDisplayStatus: function () {
            var checked_radio = this.$('input[name="pm_id"]:checked');
            if (checked_radio.data('provider') !== 'multisafepay') {
               $('input[name="multisafepay_pm_id"]').prop( "checked", false);
               $('input[name="multisafepay_pm_id"]').trigger("change");
            }

            return this._super.apply(this, arguments);
        },

        _multisafepayPayEvent: function (checked_radio) {
            checked_radio = checked_radio[0];
            var self = this;
            var acquirer_id = this.getAcquirerIdFromRadio(checked_radio);
            var acquirer_form = this.$('#o_payment_form_acq_' + acquirer_id);
            var inputs_form = $('input', acquirer_form);
            var ds = $('input[name="data_set"]', acquirer_form)[0];

            var method_id = this.$('input[name="multisafepay_pm_id"]:checked');
            var $tx_url = this.$el.find('input[name="prepare_tx_url"]');
            var invoice_id = $('input[name="invoice_id"]')
            // if there's a prepare tx url set
            if ($tx_url.length === 1) {
                // if the user wants to save his credit card info
                var form_save_token = acquirer_form.find('input[name="o_payment_form_save_token"]').prop('checked');
                // then we call the route to prepare the transaction
                var ctx = this._getContext();
                ctx = _.extend({}, ctx, {
                    "method_id": method_id.data('payment-method-id'),
                    "issuer_id": method_id.data('issuer-id'),
                    "acquirer_id": parseInt(acquirer_id),
                });
                this._rpc({
                    route: $tx_url[0].value,
                    params: {
                        'acquirer_id': parseInt(acquirer_id),
                        'save_token': form_save_token,
                        'access_token': self.options.accessToken,
                        'success_url': self.options.successUrl,
                        'error_url': self.options.errorUrl,
                        'callback_method': self.options.callbackMethod,
                        'order_id': self.options.orderId,
                        context: ctx,
                        'invoice_id': invoice_id.val(),
                    },
                }).then(function (result) {
                    if (result) {
                        // if the server sent us the html form, we create a form element
                        var newForm = document.createElement('form');
                        newForm.setAttribute("method", "post"); // set it to post
                        newForm.setAttribute("provider", checked_radio.dataset.provider);
                        newForm.hidden = true; // hide it
                        newForm.innerHTML = result; // put the html sent by the server inside the form
                        var action_url = $(newForm).find('input[name="data_set"]').data('actionUrl');
                        newForm.setAttribute("action", action_url); // set the action url
                        $(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
                        $(newForm).find('input[data-remove-me]').remove(); // remove all the input that should be removed
                        if(action_url) {
                            newForm.submit(); // and finally submit the form
                        }
                    }
                    else {
                        self.displayError(
                            _t('Server Error'),
                            _t("We are not able to redirect you to the payment form.")
                        );
                        self.enableButton(button);
                    }
                }).guardedCatch(function (error) {
                    error.event.preventDefault();
                    self.displayError(
                        _t('Server Error'),
                        _t("We are not able to redirect you to the payment form. ") +
                            self._parseError(error)
                    );
                });
            }
            else {
                // we append the form to the body and send it.
                this.displayError(
                    _t("Cannot setup the payment"),
                    _t("We're unable to process your payment.")
                );
            }

        },

        payEvent: function (ev) {
            ev.preventDefault();
            var checked_radio = this.$('input[name="pm_id"]:checked');

            if (checked_radio.length === 1 && this.isFormPaymentRadio(checked_radio)) {
                this._multisafepayPayEvent(checked_radio)
            } else {
                this._super.apply(this, arguments);
            }
        }
    });
});

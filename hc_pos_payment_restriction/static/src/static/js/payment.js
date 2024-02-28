/** @odoo-module */


import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { useBarcodeReader } from "@point_of_sale/app/barcode/barcode_reader_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
//import { PaymentTransactionPopup } from "@pos_mercury/app/payment_transaction_popup/payment_transaction_popup";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";



patch(PaymentScreen.prototype, {


    async addNewPaymentLine(paymentMethod) {
        if (paymentMethod.type == 'pay_later'){

            var active_pass = []

            for (var i = 0; i < this.pos.employees.length; i++) {

                if (this.pos.employees[i].role == 'manager'){
                    active_pass.push(this.pos.employees[i].pin)
                }

            }





            const { confirmed, payload: inputPin } = await this.popup.add(NumberPopup,
                    {
                      isPassword: true,
                      title: _t("Password?"),
                      startingValue: null,
                    }
                 );


//                 if(order.discount_applied == 'sub_manager'){

//                 var entered_input = Sha1.hash(inputPin)
//
//                 }
//                 else{
//
//                 var entered_input = parseInt(inputPin)
//
//                 }

                if (active_pass.includes(Sha1.hash(inputPin)) ||  active_pass.includes(parseInt(inputPin))){
                    const result = this.currentOrder.add_paymentline(paymentMethod);
                    if (result) {
                        this.numberBuffer.reset();
                        return true;
                    } else {
                        this.popup.add(ErrorPopup, {
                            title: _t("Error"),
                            body: _t("There is already an electronic payment in progress."),
                        });
                        return false;
                    }

                } else {
                    this.popup.add(ErrorPopup, {
                      title: _t(
                        "Incorrect Password"
                      ),
                    });
//                    return false;

                }

        }
        else{

            const result = this.currentOrder.add_paymentline(paymentMethod);
            if (result) {
                this.numberBuffer.reset();
                return true;
            } else {
                this.popup.add(ErrorPopup, {
                    title: _t("Error"),
                    body: _t("There is already an electronic payment in progress."),
                });
                return false;
            }

        }
    }


});

/** @odoo-module */


import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useBarcodeReader } from "@point_of_sale/app/barcode/barcode_reader_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";



patch(ProductScreen.prototype, {

    async onNumpadClick(buttonValue) {
       if (buttonValue === "discount") {

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


                if (active_pass.includes(Sha1.hash(inputPin)) ||  active_pass.includes(parseInt(inputPin))){
                    const result = super.onNumpadClick(buttonValue);


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

            const result = super.onNumpadClick(buttonValue);

        }
    }


});

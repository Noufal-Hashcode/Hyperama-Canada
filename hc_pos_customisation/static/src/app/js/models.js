///** @odoo-module */
/** @odoo-module **/

//import { Order } from "@point_of_sale/app/store/models";
//import { patch } from "@web/core/utils/patch";
//
//patch(Order.prototype, {
//    export_for_printing() {
//        const result = super.export_for_printing(...arguments);
//        result.is_material = this.get_product().is_package_material,
//        return result;
//    }
//});

import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Orderline.prototype, {
    setup() {
        super.setup(...arguments);
    },

    getDisplayData() {
        console.log(this.get_product().is_package,'hdshjhjfjd')
        return {
        	...super.getDisplayData(),

            is_material: this.get_product().is_package,

        };
    }
});
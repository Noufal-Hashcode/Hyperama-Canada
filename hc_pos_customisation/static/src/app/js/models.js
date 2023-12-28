///** @odoo-module */


import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
console.log('odoo mukthar')

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
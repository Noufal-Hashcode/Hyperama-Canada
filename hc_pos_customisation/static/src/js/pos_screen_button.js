/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

export class ShopifySyncButton extends Component {
    static template = "hc_pos_customisation.ShopifySyncButton";
    setup() {
        this.pos = usePos();
        this.rpc = useService("rpc");
    }
    async click() {
        try {
          const pos = this.pos;
          const rpc = this.rpc;
          const orders = await rpc("/pos/shopify_orders", {});
          for (const orderData of orders) {
            const order = pos.add_new_order();

            for (const line of orderData.lines) {
              const product = pos.db.get_product_by_id(line.product_id);
              if (product) {
                await order.add_product(product, {
                  quantity: line.qty,
                  price: line.price_unit,
                });
              }
            }

            const partner = pos.db.get_partner_by_id(orderData.partner_id);
            if (partner) {
              order.set_partner(partner);
            }

            order.shopify_order_id = orderData.order_id;
          }
        } catch (error) {
          console.error("Shopify sync failed", error);
        }
    }
}

ProductScreen.addControlButton({
    component: ShopifySyncButton,
    condition: function () {
        return this.pos.config.name === "Retail";
    },
});

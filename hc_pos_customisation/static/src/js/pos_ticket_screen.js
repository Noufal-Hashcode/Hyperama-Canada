/** @odoo-module */

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";

patch(TicketScreen.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        // Use reactive object or plain object
        this.saleOrdersByName = {};

        // Load orders before the screen is rendered
        onWillStart(async () => {
            const originIds = [
                ...new Set(
                    this.pos.orders
                        .flatMap(order => order.get_orderlines())
                        .map(line => line.sale_order_origin_id?.id)
                        .filter(Boolean)
                )
            ];
            const saleOrders = await this._getSaleOrders(originIds);
            for (const order of saleOrders) {
                if (order.name) {
                    this.saleOrdersByName[order.name] = order;
                }
            }
        });
    },

    async _getSaleOrders(ids) {
        if (!ids?.length) return [];
        const saleOrders = await this.orm.read("sale.order", ids, ["name", "shopify_order_date"]);
        return saleOrders;
    },

    getOrderValue(order) {
        // Assuming order has a line with sale_order_origin_id
        const line = order.get_orderlines().find(l => l.sale_order_origin_id?.id);
        const saleOrderName = line?.sale_order_origin_id?.name;

        if (!saleOrderName) {
            return {
                name: "Manually Created",
                date: false,
            };
        }

        const saleOrder = this.saleOrdersByName[saleOrderName];
        return {
            name: saleOrder?.name || "Manually Created",
            date: saleOrder?.shopify_order_date || '/' ,
        };
    },
});


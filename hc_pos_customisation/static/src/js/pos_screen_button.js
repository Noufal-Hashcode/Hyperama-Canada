/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { Orderline } from "@point_of_sale/app/store/models";
import { floatIsZero } from "@web/core/utils/numbers";

/**
 * ID getter to take into account falsy many2one value.
 * @param {[id: number, display_name: string] | false} fieldVal many2one field value
 * @returns {number | false}
 */
function getId(fieldVal) {
    return fieldVal && fieldVal[0];
}

export class ShopifySyncButton extends Component {
    static template = "hc_pos_customisation.ShopifySyncButton";
    
    setup() {
        this.pos = usePos();
        this.rpc = useService("rpc");
        this.popup = useService("popup");
        this.orm = useService("orm");
        this.notification = useService("pos_notification");
    }

    async click() {
        try {
            this.notification.add(_t("Syncing Shopify orders..."), 2000);
            
            // Fetch and process Shopify orders directly
            await this.fetchAndSettleShopifyOrders();
            
        } catch (error) {
            console.error("Shopify sync failed", error);
            await this.popup.add(ErrorPopup, {
                title: _t("Sync Error"),
                body: _t("Failed to sync Shopify orders: %s", error.message || error)
            });
        }
    }

    async fetchAndSettleShopifyOrders() {
        let offset = 0;
        const limit = 50;
        let processedCount = 0;

        while (true) {
            // Fetch orders from Python endpoint
            const orders = await this.rpc("/pos/shopify_orders", { limit, offset });
            if (!orders.length) break;

            for (const orderData of orders) {
                try {
                    await this.settleShopifyOrder(orderData);
                    processedCount++;
                } catch (error) {
                    console.error(`Failed to process order ${orderData.order_id}:`, error);
                    // Continue with next order even if one fails
                }
            }

            offset += limit;
        }

        if (processedCount > 0) {
            this.notification.add(_t("%s Shopify orders processed and settled successfully.", processedCount), 4000);
        } else {
            this.notification.add(_t("No new Shopify orders to process."), 4000);
        }
    }

    async settleShopifyOrder(orderData) {
        // Create new POS order for each Shopify order
        let currentPOSOrder = this.pos.add_new_order();

        // Set partner if available
        if (orderData.partner_id) {
            let order_partner = this.pos.db.get_partner_by_id(orderData.partner_id);
            if (!order_partner) {
                try {
                    await this.pos._loadPartners([orderData.partner_id]);
                    order_partner = this.pos.db.get_partner_by_id(orderData.partner_id);
                } catch (error) {
                    console.error(`Failed to load partner ${orderData.partner_id}:`, error);
                }
            }
            if (order_partner) {
                currentPOSOrder.set_partner(order_partner);
            }
        }

        // Set fiscal position if available
        if (orderData.fiscal_position_id) {
            const orderFiscalPos = this.pos.fiscal_positions.find(
                (position) => position.id === orderData.fiscal_position_id
            );
            if (orderFiscalPos) {
                currentPOSOrder.fiscal_position = orderFiscalPos;
            }
        }

        // Set pricelist if available
        if (orderData.pricelist_id) {
            const orderPricelist = this.pos.pricelists.find(
                (pricelist) => pricelist.id === orderData.pricelist_id
            );
            if (orderPricelist) {
                currentPOSOrder.set_pricelist(orderPricelist);
            }
        }

        // Check if products need to be loaded
        const product_to_add_in_pos = orderData.lines
            .filter((line) => !this.pos.db.get_product_by_id(line.product_id))
            .map((line) => line.product_id);

        if (product_to_add_in_pos.length) {
            try {
                await this.pos._addProducts(product_to_add_in_pos);
            } catch (error) {
                console.error("Failed to load some products:", error);
            }
        }

        // Process each line and settle the order
        for (const line of orderData.lines) {
            const product = this.pos.db.get_product_by_id(line.product_id);
            if (!product) {
                continue;
            }

            const line_values = {
                pos: this.pos,
                order: currentPOSOrder,
                product: product,
                description: line.name || product.display_name,
                price: line.price_unit || product.list_price,
                tax_ids: line.tax_ids || product.taxes_id,
                price_manually_set: false,
                price_type: "automatic",
                sale_order_origin_id: {
                    id: orderData.order_id,
                    name: orderData.name || `Shopify-${orderData.order_id}`,
                },
                shopify_order_date: orderData.order_date,
                customer_note: line.customer_note || '',
            };

            const new_line = new Orderline({ env: this.env }, line_values);

            // Handle lot/serial numbers if available
            if (
                product.tracking !== "none" &&
                (this.pos.picking_type.use_create_lots || this.pos.picking_type.use_existing_lots) &&
                line.lot_names && line.lot_names.length > 0
            ) {
                new_line.setPackLotLines({
                    modifiedPackLotLines: [],
                    newPackLotLines: line.lot_names.map((name) => ({
                        lot_name: name,
                    })),
                });
            }

            // Set quantity and pricing
            const quantity = line.qty || line.product_uom_qty || 1;
            new_line.set_quantity(quantity, true);
            new_line.set_unit_price(line.price_unit || product.list_price);
            
            if (line.discount) {
                new_line.set_discount(line.discount);
            }

            // Handle non-groupable units (split if necessary)
            const product_unit = product.get_unit();
            if (product_unit && !product.get_unit().is_pos_groupable) {
                let remaining_quantity = quantity;
                while (!floatIsZero(remaining_quantity, 6)) {
                    const splitted_line = new Orderline({ env: this.env }, line_values);
                    const qty_to_add = Math.min(remaining_quantity, 1.0);
                    splitted_line.set_quantity(qty_to_add, true);
                    if (line.discount) {
                        splitted_line.set_discount(line.discount);
                    }
                    currentPOSOrder.add_orderline(splitted_line);
                    remaining_quantity -= qty_to_add;
                }
            } else {
                currentPOSOrder.add_orderline(new_line);
            }
        }

        // Set order reference/note for Shopify
        if (orderData.order_id) {
            currentPOSOrder.set_note(`Shopify Order: ${orderData.order_id}${orderData.order_date ? ` (${orderData.order_date})` : ''}`);
        }

        // Mark order as settled (this will be the active order ready for payment)
        this.notification.add(_t("Shopify order %s added to POS and ready for payment.", orderData.order_id || orderData.name), 3000);
    }

    _getSaleOrderOrigin(order) {
        for (const line of order.get_orderlines()) {
            if (line.sale_order_origin_id) {
                return line.sale_order_origin_id;
            }
        }
        return false;
    }
}

ProductScreen.addControlButton({
    component: ShopifySyncButton,
    condition: function () {
        return this.pos.config.name === "Retail";
    },
});
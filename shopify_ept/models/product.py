# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo import models, fields, _
from odoo.exceptions import UserError
import logging
import time

_logger = logging.getLogger("Shopify Operations")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopify_instance_id = fields.Many2one("shopify.instance.ept")
    export_to_shopify = fields.Boolean(string='Export to Shopify', default=False)

    # server action
    def action_shopify(self):
        for rec in self:
            shopify_product =self.env['shopify.product.template.ept'].search([('product_tmpl_id','=',rec.id)])
            if shopify_product:
                rec.export_to_shopify=True
                rec.shopify_instance_id =shopify_product.shopify_instance_id
    def manual_update_product_to_shopify(self):
        """ This method is used to call child method for update products values from shopify layer products to Shopify
            store. It calls from the Shopify layer product screen.
        """
        # if not self.shopify_is_update_basic_detail and not self.shopify_is_publish and not self.shopify_is_set_price \
        #         and not self.shopify_is_set_image:
        #     raise UserError("Please Select Any Option To Update Product.")

        shopify_product_template_obj = self.env['shopify.product.template.ept']
        shopify_product_obj = self.env['shopify.product.product.ept']
        instance_obj = self.env['shopify.instance.ept']
        product_obj = self.env['product.product'].search([('product_tmpl_id','=',self.id)])
        var = shopify_product_obj.search([('product_id','=',product_obj.id)])
        var.default_code=self.default_code
        var.name=self.name
        product_template_ept = shopify_product_template_obj.search([('product_tmpl_id','=',self.id)])
        product_template_ept.name = self.name


        start = time.time()
        shopify_products = self._context.get('active_ids', [])
        template = shopify_product_template_obj.search([('product_tmpl_id','=',self.id)])

        # template = shopify_product_template_obj.browse(shopify_products)
        # templates = template.filtered(lambda x: x.exported_in_shopify)
        # if templates and len(templates) > 80:
        #     raise UserError(_("Error:\n- System will not update more then 80 Products at a "
        #                       "time.\n- Please select only 80 product for export."))
        shopify_instances = instance_obj.search([])
        # for instance in shopify_instances:
        shopify_templates = template.filtered(lambda product: product.shopify_instance_id == self.shopify_instance_id)
        if shopify_templates:
            shopify_product_obj.update_products_in_shopify(self.shopify_instance_id, shopify_templates,
                                                          True,
                                                           True,
                                                          True,
                                                           True)
        end = time.time()
        _logger.info("Update Processed %s Products in %s seconds.", str(len(template)), str(end - start))

        return True

    def export_direct_in_shopify(self, product_templates):
        """
        Creates new products or updates existing products in the Shopify layer using the direct export method.
        @author: Maulik Barad on Date 19-Sep-2020.
        """
        shopify_template_id = False
        sequence = 0
        variants = product_templates.product_variant_ids
        shopify_instance = self.shopify_instance_id

        for variant in variants:
            if not variant.default_code:
                continue
            product_template = variant.product_tmpl_id
            if product_template.attribute_line_ids and len(product_template.attribute_line_ids.filtered(
                    lambda x: x.attribute_id.create_variant == "always")) > 3:
                continue
            shopify_template, sequence, shopify_template_id = self.create_or_update_shopify_layer_template(
                shopify_instance, product_template, variant, shopify_template_id, sequence)

            self.create_shopify_template_images(shopify_template)

            if shopify_template and shopify_template.shopify_product_ids and \
                    shopify_template.shopify_product_ids[0].sequence:
                sequence += 1

            shopify_variant = self.create_or_update_shopify_layer_variant(variant, shopify_template_id,
                                                                          shopify_instance, shopify_template, sequence)

            self.create_shopify_variant_images(shopify_template, shopify_variant)
        return True

    def create_or_update_shopify_layer_template(self, shopify_instance, product_template, variant,
                                                shopify_template_id, sequence):
        """ This method is used to create or update the Shopify layer template.
            @return: shopify_template, sequence, shopify_template_id
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 26 October 2020 .
            Task_id: 167537 - Code refactoring
        """
        shopify_templates = shopify_template_obj = self.env["shopify.product.template.ept"]

        shopify_template = shopify_template_obj.search([
            ("shopify_instance_id", "=", shopify_instance.id),
            ("product_tmpl_id", "=", product_template.id)], limit=1)

        if not shopify_template:
            shopify_product_template_vals = self.prepare_template_val_for_export_product_in_layer(product_template,
                                                                                                  shopify_instance,
                                                                                                  variant)
            shopify_template = shopify_template_obj.create(shopify_product_template_vals)
            sequence = 1
            shopify_template_id = shopify_template.id
        else:
            if shopify_template_id != shopify_template.id:
                shopify_product_template_vals = self.prepare_template_val_for_export_product_in_layer(product_template,
                                                                                                      shopify_instance,
                                                                                                      variant)
                shopify_template.write(shopify_product_template_vals)
                shopify_template_id = shopify_template.id
        if shopify_template not in shopify_templates:
            shopify_templates += shopify_template

        return shopify_template, sequence, shopify_template_id

    def create_shopify_template_images(self, shopify_template):
        """
        For adding all odoo images into shopify layer only for template.
        @author: Maulik Barad on Date 19-Sep-2020.
        """
        shopify_product_image_list = []
        shopify_product_image_obj = self.env["shopify.product.image.ept"]

        product_template = shopify_template.product_tmpl_id
        for odoo_image in product_template.ept_image_ids.filtered(lambda x: not x.product_id):
            shopify_product_image = shopify_product_image_obj.search_read(
                [("shopify_template_id", "=", shopify_template.id),
                 ("odoo_image_id", "=", odoo_image.id)], ["id"])
            if not shopify_product_image:
                shopify_product_image_list.append({
                    "odoo_image_id": odoo_image.id,
                    "shopify_template_id": shopify_template.id
                })
        if shopify_product_image_list:
            shopify_product_image_obj.create(shopify_product_image_list)
        return True

    def create_or_update_shopify_layer_variant(self, variant, shopify_template_id, shopify_instance,
                                               shopify_template, sequence):
        """ This method is used to create/update the variant in the shopify layer.
            @return: shopify_variant
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 26 October 2020 .
            Task_id: 167537 - Code refactoring
        """
        shopify_product_obj = self.env["shopify.product.product.ept"]

        shopify_variant = shopify_product_obj.search([
            ("shopify_instance_id", "=", self.shopify_instance_id.id),
            ("product_id", "=", variant.id),
            ("shopify_template_id", "=", shopify_template_id)])

        shopify_variant_vals = self.prepare_variant_val_for_export_product_in_layer(shopify_instance,
                                                                                    shopify_template, variant,
                                                                                    sequence)
        if not shopify_variant:
            shopify_variant = shopify_product_obj.create(shopify_variant_vals)
        else:
            shopify_variant.write(shopify_variant_vals)

        return shopify_variant
    def create_shopify_variant_images(self, shopify_template, shopify_variant):
        """
        For adding first odoo image into shopify layer for variant.
        @author: Maulik Barad on Date 19-Sep-2020.
        """
        shopify_product_image_obj = self.env["shopify.product.image.ept"]
        product_id = shopify_variant.product_id
        odoo_image = product_id.ept_image_ids
        if odoo_image:
            shopify_product_image = shopify_product_image_obj.search_read(
                [("shopify_template_id", "=", shopify_template.id),
                 ("shopify_variant_id", "=", shopify_variant.id),
                 ("odoo_image_id", "=", odoo_image[0].id)], ["id"])
            if not shopify_product_image:
                shopify_product_image_obj.create({
                    "odoo_image_id": odoo_image[0].id,
                    "shopify_variant_id": shopify_variant.id,
                    "shopify_template_id": shopify_template.id,
                    "sequence": 0
                })
        return True
    def prepare_template_val_for_export_product_in_layer(self, product_template, shopify_instance, variant):
        """ This method is used to prepare a template Vals for export/update product
            from Odoo products to the Shopify products layer.
            :param product_template: Record of odoo template.
            :param product_template: Record of instance.
            @return: template_vals
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 26 October 2020 .
            Task_id: 167537 - Code refactoring
        """
        ir_config_parameter_obj = self.env["ir.config_parameter"]
        template_vals = {"product_tmpl_id": product_template.id,
                         "shopify_instance_id": shopify_instance.id,
                         "shopify_product_category": product_template.categ_id.id,
                         "name": product_template.name}
        if ir_config_parameter_obj.sudo().get_param("shopify_ept.set_sales_description"):
            template_vals.update({"description": variant.description_sale})
        return template_vals

    def prepare_variant_val_for_export_product_in_layer(self, shopify_instance, shopify_template, variant, sequence):
        """ This method is used to prepare a vals for the variants.
            @return: shopify_variant_vals
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 26 October 2020 .
            Task_id: 167537 - Code refactoring
        """
        shopify_variant_vals = ({
            "shopify_instance_id": shopify_instance.id,
            "product_id": variant.id,
            "shopify_template_id": shopify_template.id,
            "default_code": variant.default_code,
            "name": variant.name,
            "sequence": sequence
        })
        return shopify_variant_vals



    def manual_export_product_to_shopify(self,product_template):
        """ This method is used to call child method for export products from shopify layer products to Shopify store.
            It calls from the Shopify layer product screen.
        """
        start = time.time()
        shopify_product_template_obj = self.env["shopify.product.template.ept"]
        shopify_product_obj = self.env['shopify.product.product.ept']
        instance_obj = self.env['shopify.instance.ept']

        # shopify_products = self._context.get('active_ids', [])
        shopify_products= self.env["shopify.product.template.ept"].search([('product_tmpl_id','=',product_template.id)])

        template = shopify_product_template_obj.browse(shopify_products.id)
        templates = template.filtered(lambda x: not x.exported_in_shopify)
        # if templates and len(templates) > 80:
        #     raise UserError(_("Error:\n- System will not export more then 80 Products at a "
        #                       "time.\n- Please select only 80 product for export."))
        shopify_instances = instance_obj.search([])
        for instance in shopify_instances:
            shopify_templates = templates.filtered(lambda product: product.shopify_instance_id == instance)
            if shopify_templates:
                shopify_product_obj.shopify_export_products(instance,
                                                            True,
                                                            True,
                                                            True,
                                                            True,
                                                            shopify_templates)
        end = time.time()
        _logger.info("Export Processed %s Products in %s seconds.", str(len(templates)), str(end - start))
        return True


    def write(self, vals):
        """
        This method use to archive/unarchive shopify product templates base on odoo product templates.
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 09/12/2019.
        :Task id: 158502
        """
        # if self.export_to_shopify:
        #     product_templates = self.filtered(lambda template: template.detailed_type == "product")
        #     if not product_templates:
        #         raise UserError(_("It seems like selected products are not Storable products."))
        #
        #
        #     self.export_direct_in_shopify(product_templates)
        if 'active' in vals.keys():
            shopify_product_template_obj = self.env['shopify.product.template.ept']
            for template in self:
                shopify_templates = shopify_product_template_obj.search(
                    [('product_tmpl_id', '=', template.id)])
                if vals.get('active'):
                    shopify_templates = shopify_product_template_obj.search(
                        [('product_tmpl_id', '=', template.id), ('active', '=', False)])
                shopify_templates.write({'active': vals.get('active')})
        res = super(ProductTemplate, self).write(vals)
        if self.export_to_shopify == True:
            if not self.detailed_type == "product":
                raise UserError(_("It seems like selected products are not Storable products."))
            shopify_products = self.env["shopify.product.template.ept"].search(
                [('product_tmpl_id', '=', self.id)])
            # self.manual_export_product_to_shopify(self)

            if not shopify_products:
                self.export_direct_in_shopify(self)
                self.manual_export_product_to_shopify(self)
            else:
                self.manual_update_product_to_shopify()

        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    shopify_instance_id = fields.Many2one("shopify.instance.ept")
    export_to_shopify = fields.Boolean(string='Export to Shopify', default=False)

    def write(self, vals):
        """
        This method use to archive/unarchive shopify product base on odoo product.
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 30/03/2019.
        """
        if 'active' in vals.keys():
            shopify_product_product_obj = self.env['shopify.product.product.ept']
            for product in self:
                shopify_product = shopify_product_product_obj.search(
                    [('product_id', '=', product.id)])
                if vals.get('active'):
                    shopify_product = shopify_product_product_obj.search(
                        [('product_id', '=', product.id), ('active', '=', False)])
                shopify_product.write({'active': vals.get('active')})
        res = super(ProductProduct, self).write(vals)
        if self.export_to_shopify == True:
            if not self.detailed_type == "product":
                raise UserError(_("It seems like selected products are not Storable products."))
            shopify_products = self.env["shopify.product.template.ept"].search(
                [('product_tmpl_id', '=', self.product_tmpl_id.id)])

            if not shopify_products:
                self.export_direct_in_shopify(self.product_tmpl_id)
                self.manual_export_product_to_shopify(self.product_tmpl_id)

            else:
                self.manual_update_product_to_shopify()

        # return res
        return res

    def export_direct_in_shopify(self, product_templates):
        """
        Creates new products or updates existing products in the Shopify layer using the direct export method.
        @author: Maulik Barad on Date 19-Sep-2020.
        """
        shopify_template_id = False
        sequence = 0
        variants = product_templates.product_variant_ids
        shopify_instance = self.shopify_instance_id

        for variant in variants:
            if not variant.default_code:
                continue
            product_template = variant.product_tmpl_id
            if product_template.attribute_line_ids and len(product_template.attribute_line_ids.filtered(
                    lambda x: x.attribute_id.create_variant == "always")) > 3:
                continue
            shopify_template, sequence, shopify_template_id = self.create_or_update_shopify_layer_template(
                shopify_instance, product_template, variant, shopify_template_id, sequence)

            self.create_shopify_template_images(shopify_template)

            if shopify_template and shopify_template.shopify_product_ids and \
                    shopify_template.shopify_product_ids[0].sequence:
                sequence += 1

            shopify_variant = self.create_or_update_shopify_layer_variant(variant, shopify_template_id,
                                                                          shopify_instance, shopify_template, sequence)

            self.create_shopify_variant_images(shopify_template, shopify_variant)
        return True

    def create_or_update_shopify_layer_template(self, shopify_instance, product_template, variant,
                                                shopify_template_id, sequence):
        """ This method is used to create or update the Shopify layer template.
            @return: shopify_template, sequence, shopify_template_id
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 26 October 2020 .
            Task_id: 167537 - Code refactoring
        """
        shopify_templates = shopify_template_obj = self.env["shopify.product.template.ept"]

        shopify_template = shopify_template_obj.search([
            ("shopify_instance_id", "=", shopify_instance.id),
            ("product_tmpl_id", "=", product_template.id)], limit=1)

        if not shopify_template:
            shopify_product_template_vals = self.prepare_template_val_for_export_product_in_layer(product_template,
                                                                                                  shopify_instance,
                                                                                                  variant)
            shopify_template = shopify_template_obj.create(shopify_product_template_vals)
            sequence = 1
            shopify_template_id = shopify_template.id
        else:
            if shopify_template_id != shopify_template.id:
                shopify_product_template_vals = self.prepare_template_val_for_export_product_in_layer(product_template,
                                                                                                      shopify_instance,
                                                                                                      variant)
                shopify_template.write(shopify_product_template_vals)
                shopify_template_id = shopify_template.id
        if shopify_template not in shopify_templates:
            shopify_templates += shopify_template

        return shopify_template, sequence, shopify_template_id

    def create_shopify_template_images(self, shopify_template):
        """
        For adding all odoo images into shopify layer only for template.
        @author: Maulik Barad on Date 19-Sep-2020.
        """
        shopify_product_image_list = []
        shopify_product_image_obj = self.env["shopify.product.image.ept"]

        product_template = shopify_template.product_tmpl_id
        for odoo_image in product_template.ept_image_ids.filtered(lambda x: not x.product_id):
            shopify_product_image = shopify_product_image_obj.search_read(
                [("shopify_template_id", "=", shopify_template.id),
                 ("odoo_image_id", "=", odoo_image.id)], ["id"])
            if not shopify_product_image:
                shopify_product_image_list.append({
                    "odoo_image_id": odoo_image.id,
                    "shopify_template_id": shopify_template.id
                })
        if shopify_product_image_list:
            shopify_product_image_obj.create(shopify_product_image_list)
        return True

    def create_or_update_shopify_layer_variant(self, variant, shopify_template_id, shopify_instance,
                                               shopify_template, sequence):
        """ This method is used to create/update the variant in the shopify layer.
            @return: shopify_variant
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 26 October 2020 .
            Task_id: 167537 - Code refactoring
        """
        shopify_product_obj = self.env["shopify.product.product.ept"]

        shopify_variant = shopify_product_obj.search([
            ("shopify_instance_id", "=", self.shopify_instance_id.id),
            ("product_id", "=", variant.id),
            ("shopify_template_id", "=", shopify_template_id)])

        shopify_variant_vals = self.prepare_variant_val_for_export_product_in_layer(shopify_instance,
                                                                                    shopify_template, variant,
                                                                                    sequence)
        if not shopify_variant:
            shopify_variant = shopify_product_obj.create(shopify_variant_vals)
        else:
            shopify_variant.write(shopify_variant_vals)

        return shopify_variant
    def create_shopify_variant_images(self, shopify_template, shopify_variant):
        """
        For adding first odoo image into shopify layer for variant.
        @author: Maulik Barad on Date 19-Sep-2020.
        """
        shopify_product_image_obj = self.env["shopify.product.image.ept"]
        product_id = shopify_variant.product_id
        odoo_image = product_id.ept_image_ids
        if odoo_image:
            shopify_product_image = shopify_product_image_obj.search_read(
                [("shopify_template_id", "=", shopify_template.id),
                 ("shopify_variant_id", "=", shopify_variant.id),
                 ("odoo_image_id", "=", odoo_image[0].id)], ["id"])
            if not shopify_product_image:
                shopify_product_image_obj.create({
                    "odoo_image_id": odoo_image[0].id,
                    "shopify_variant_id": shopify_variant.id,
                    "shopify_template_id": shopify_template.id,
                    "sequence": 0
                })
        return True
    def prepare_template_val_for_export_product_in_layer(self, product_template, shopify_instance, variant):
        """ This method is used to prepare a template Vals for export/update product
            from Odoo products to the Shopify products layer.
            :param product_template: Record of odoo template.
            :param product_template: Record of instance.
            @return: template_vals
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 26 October 2020 .
            Task_id: 167537 - Code refactoring
        """
        ir_config_parameter_obj = self.env["ir.config_parameter"]
        template_vals = {"product_tmpl_id": product_template.id,
                         "shopify_instance_id": shopify_instance.id,
                         "shopify_product_category": product_template.categ_id.id,
                         "name": product_template.name}
        if ir_config_parameter_obj.sudo().get_param("shopify_ept.set_sales_description"):
            template_vals.update({"description": variant.description_sale})
        return template_vals

    def prepare_variant_val_for_export_product_in_layer(self, shopify_instance, shopify_template, variant, sequence):
        """ This method is used to prepare a vals for the variants.
            @return: shopify_variant_vals
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 26 October 2020 .
            Task_id: 167537 - Code refactoring
        """
        shopify_variant_vals = ({
            "shopify_instance_id": shopify_instance.id,
            "product_id": variant.id,
            "shopify_template_id": shopify_template.id,
            "default_code": variant.default_code,
            "name": variant.name,
            "sequence": sequence
        })
        return shopify_variant_vals



    def manual_export_product_to_shopify(self,product_template):
        """ This method is used to call child method for export products from shopify layer products to Shopify store.
            It calls from the Shopify layer product screen.
        """
        start = time.time()
        shopify_product_template_obj = self.env["shopify.product.template.ept"]
        shopify_product_obj = self.env['shopify.product.product.ept']
        instance_obj = self.env['shopify.instance.ept']

        # shopify_products = self._context.get('active_ids', [])
        shopify_products= self.env["shopify.product.template.ept"].search([('product_tmpl_id','=',product_template.id)])

        template = shopify_product_template_obj.browse(shopify_products.id)
        templates = template.filtered(lambda x: not x.exported_in_shopify)
        # if templates and len(templates) > 80:
        #     raise UserError(_("Error:\n- System will not export more then 80 Products at a "
        #                       "time.\n- Please select only 80 product for export."))
        shopify_instances = instance_obj.search([])
        for instance in shopify_instances:
            shopify_templates = templates.filtered(lambda product: product.shopify_instance_id == instance)
            if shopify_templates:
                shopify_product_obj.shopify_export_products(instance,
                                                            True,
                                                            True,
                                                            True,
                                                            True,
                                                            shopify_templates)
        end = time.time()
        _logger.info("Export Processed %s Products in %s seconds.", str(len(templates)), str(end - start))
        return True

    # def manual_update_product_to_shopify(self):
    #     """ This method is used to call child method for update products values from shopify layer products to Shopify
    #         store. It calls from the Shopify layer product screen.
    #     """
    #     # if not self.shopify_is_update_basic_detail and not self.shopify_is_publish and not self.shopify_is_set_price \
    #     #         and not self.shopify_is_set_image:
    #     #     raise UserError("Please Select Any Option To Update Product.")
    #
    #     shopify_product_template_obj = self.env['shopify.product.template.ept']
    #     shopify_product_obj = self.env['shopify.product.product.ept']
    #     instance_obj = self.env['shopify.instance.ept']
    #
    #     start = time.time()
    #     # shopify_products = self._context.get('active_ids', [])
    #     template = shopify_product_template_obj.search([('product_tmpl_id','=',self.product_tmpl_id)])
    #
    #     # template = shopify_product_template_obj.browse(shopify_products)
    #     templates = template.filtered(lambda x: x.exported_in_shopify)
    #     # if templates and len(templates) > 80:
    #     #     raise UserError(_("Error:\n- System will not update more then 80 Products at a "
    #     #                       "time.\n- Please select only 80 product for export."))
    #     shopify_instances = instance_obj.search([])
    #     for instance in shopify_instances:
    #         shopify_templates = templates.filtered(lambda product: product.shopify_instance_id == instance)
    #         if shopify_templates:
    #             shopify_product_obj.update_products_in_shopify(instance, shopify_templates,
    #                                                           True,
    #                                                            True,
    #                                                            True,
    #                                                            True,
    #                                                            )
    #     end = time.time()
    #     _logger.info("Update Processed %s Products in %s seconds.", str(len(template)), str(end - start))
    #     return True



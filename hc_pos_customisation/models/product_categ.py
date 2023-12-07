# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.tools import float_round, groupby


class ProductCategory(models.Model):
    _inherit = 'product.category'


    is_package_material = fields.Boolean(string='Is Package Material',)


# class ProductTemplate(models.Model):
#     _inherit = 'product.template'
#
#
#     is_package_material = fields.Boolean(string='Is Package Material', compute="_compute_is_package_material",store=True)
#
#     def _compute_is_package_material(self):
#         for item in self:
#             if item.categ_id.is_package_material==True:
#                 item.is_package_material=True
#             else:
#                 item.is_package_material=False
#
#         return
class ProductProduct(models.Model):
    _inherit = 'product.product'


    is_package = fields.Boolean(string='Is Package Material', related='categ_id.is_package_material')

    def _compute_is_package(self):
        for item in self:
            if item.categ_id.is_package_material==True:
                item.is_package=True
            else:
                item.is_package=False
        # self.is_package = True
        return


# class PosOrderLine(models.Model):
#     _inherit = 'pos.order.line'
#
#     line_image = fields.Boolean(string='Is Package Material',default=True,store=True )
#     # line_image = fields.Binary(string="Product Image",related='product_id.product_tmpl_id.is_package_material',store=True)
#
#     def _compute_is_package_materials(self):
#         for i in self:
#             # if i.product_id.product_tmpl_id.categ_id.is_package_material == True:
#             i.line_image = True
#             # else:
#             #     i.line_image = False
#
#             return


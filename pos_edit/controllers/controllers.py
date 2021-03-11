# -*- coding: utf-8 -*-
from odoo import http

# class PosEdit(http.Controller):
#     @http.route('/pos_edit/pos_edit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_edit/pos_edit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_edit.listing', {
#             'root': '/pos_edit/pos_edit',
#             'objects': http.request.env['pos_edit.pos_edit'].search([]),
#         })

#     @http.route('/pos_edit/pos_edit/objects/<model("pos_edit.pos_edit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_edit.object', {
#             'object': obj
#         })
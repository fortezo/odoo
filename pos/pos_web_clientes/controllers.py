# -*- coding: utf-8 -*-
from openerp import http

# class ClientesPosWeb(http.Controller):
#     @http.route('/clientes_pos_web/clientes_pos_web/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/clientes_pos_web/clientes_pos_web/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('clientes_pos_web.listing', {
#             'root': '/clientes_pos_web/clientes_pos_web',
#             'objects': http.request.env['clientes_pos_web.clientes_pos_web'].search([]),
#         })

#     @http.route('/clientes_pos_web/clientes_pos_web/objects/<model("clientes_pos_web.clientes_pos_web"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('clientes_pos_web.object', {
#             'object': obj
#         })
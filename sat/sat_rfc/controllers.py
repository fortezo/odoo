# -*- coding: utf-8 -*-
from openerp import http

# class Rfc(http.Controller):
#     @http.route('/rfc/rfc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rfc/rfc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rfc.listing', {
#             'root': '/rfc/rfc',
#             'objects': http.request.env['rfc.rfc'].search([]),
#         })

#     @http.route('/rfc/rfc/objects/<model("rfc.rfc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rfc.object', {
#             'object': obj
#         })
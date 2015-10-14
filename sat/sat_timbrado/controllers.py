# -*- coding: utf-8 -*-
from openerp import http

# class CfdiConfig(http.Controller):
#     @http.route('/cfdi_config/cfdi_config/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cfdi_config/cfdi_config/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cfdi_config.listing', {
#             'root': '/cfdi_config/cfdi_config',
#             'objects': http.request.env['cfdi_config.cfdi_config'].search([]),
#         })

#     @http.route('/cfdi_config/cfdi_config/objects/<model("cfdi_config.cfdi_config"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cfdi_config.object', {
#             'object': obj
#         })
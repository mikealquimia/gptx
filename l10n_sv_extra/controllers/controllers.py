# -*- coding: utf-8 -*-
from odoo import http

# class L10SvExtra(http.Controller):
#     @http.route('/l10_sv_extra/l10_sv_extra/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10_sv_extra/l10_sv_extra/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10_sv_extra.listing', {
#             'root': '/l10_sv_extra/l10_sv_extra',
#             'objects': http.request.env['l10_sv_extra.l10_sv_extra'].search([]),
#         })

#     @http.route('/l10_sv_extra/l10_sv_extra/objects/<model("l10_sv_extra.l10_sv_extra"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10_sv_extra.object', {
#             'object': obj
#         })
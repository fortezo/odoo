# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow,api
from itertools import ifilter

import amount_to_text_es_MX



class account_regimen_fiscal(osv.Model):
	_name = 'account.regimen.fiscal'
	_columns = {
	    'name': fields.char(
	        'Regimen Fiscal',
	    ),
	}
class account_invoice_sat(osv.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    def _cfdi_cantidad_con_letra(self, cr, uid, ids, field_names, arg, context=None):
        res = dict([(i, {}) for i in ids])
        for line in self.browse(cr, uid, ids, context=context):
            amount_to_text = amount_to_text_es_MX.get_amount_to_text(self, line.amount_total, 'es_cheque', 'code' in line.currency_id._columns and line.currency_id.code or line.currency_id.name)

            res[line.id]['cfdi_cantidad_con_letra'] = amount_to_text
        return res
    _columns = {
        'cfdi_qr':fields.binary('QR'),
        'cfdi_xml':fields.binary('XML'),
    	'cfdi_NumSerieCerSAT':fields.char('Numero de Cerie del SAT',copy=False,help="Requerimiento Fiscal", readonly=True),
    	'cfdi_NumSerieCer':fields.char('Numero de Cerie del Certificado',copy=False,help="Requerimiento Fiscal",readonly=True),
    	'cfdi_Fecha':fields.char('Fecha de Validacion',copy=False,help="Requerimiento Fiscal",readonly=True),
    	'cfdi_SelloCFDI':fields.char('Sello del CFDI',copy=False,help="Requerimiento Fiscal",readonly=True),
    	'cfdi_SelloSAT':fields.char('Sello del SAT',copy=False,help="Requerimiento Fiscal",readonly=True),
    	'cfdi_CadenaOri':fields.char('Cadena Original',copy=False,help="Requerimiento Fiscal",readonly=True),
    	'cfdi_SerieFolioFiscal':fields.char('UUID',copy=False,help="Requerimiento Fiscal",readonly=True),
        'cfdi_cantidad_con_letra': fields.function(_cfdi_cantidad_con_letra,type='char',multi='cfdi_cantidad_con_letra', string='Total del Pedido', store=False),

    }
    @api.multi
    def invoice_validate(self):

        invoice_obj = self.env['acount.invoice.getcfdi']
        invoice_obj._get_cfdi(self)
        return True

class res_partner_sat(osv.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
    	'regimen_fiscal': fields.many2one('account.regimen.fiscal', 'Regimen Fiscal', change_default=True, select=True, track_visibility='always'),
        'razon_social': fields.char('Razon Social'),
    }

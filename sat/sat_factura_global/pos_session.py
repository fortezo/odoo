# -*- coding: utf-8 -*-

import logging
import time
from datetime import datetime

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
import openerp.addons.product.product

_logger = logging.getLogger(__name__)

class factura_global_config(osv.osv):
    _name = 'factura.global.config'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Cliente'),
        'company_id':fields.many2one('res.company', 'Sucursal')
    }

class pos_session(osv.osv):
	_name = 'pos.session'
	_inherit = 'pos.session'
	_columns = {
            'factura_id': fields.many2one('account.invoice','Factura'),
        }

	def wkf_action_close(self, cr, uid, ids, context=None):
        # Close CashBox
		inv_ref = self.pool.get('account.invoice')
		config = self.pool.get('factura.global.config')
		inv_line_ref = self.pool.get('account.invoice.line')
		product_obj = self.pool.get('product.product')

		for session in self.browse(cr, uid, ids, context=None):
			config_id = config.search(cr, uid, [('company_id', '=', self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id)], context=None)[0]
			config_obj = config.browse(cr, uid, [config_id], context=None)[0]

			acc = config_obj.partner_id.property_account_receivable.id
			inv = {
	                'name': session.name,
	                'origin': session.name,
	                'account_id': acc,
	                'type': 'out_invoice',
	                'reference': session.name,
	                'partner_id': config_obj.partner_id.id,
	                'comment': 'Factura global de corte de caja',
	            }

			inv_id = inv_ref.create(cr, uid, inv, context=context)
			for order in session.order_ids:
				for line in order.lines:
					inv_line = {
	                    'invoice_id': inv_id,
	                    'product_id': line.product_id.id,
	                    'quantity': line.qty,
                	}
					inv_name = product_obj.name_get(cr, uid, [line.product_id.id], context=context)[0][1]
					inv_line.update(inv_line_ref.product_id_change(cr, uid, [],line.product_id.id,line.product_id.uom_id.id,line.qty, partner_id = config_obj.partner_id.id,fposition_id=config_obj.partner_id.property_account_position.id)['value'])
					if not inv_line.get('account_analytic_id', False):
						inv_line['account_analytic_id'] = False
					inv_line['price_unit'] = line.price_unit
					inv_line['discount'] = line.discount
					inv_line['name'] = inv_name
					inv_line['invoice_line_tax_id'] = [(6, 0, inv_line['invoice_line_tax_id'])]
					inv_line_ref.create(cr, uid, inv_line, context=context)
			inv_ref.button_reset_taxes(cr, uid, [inv_id], context=context)
			#self.signal_workflow(cr, uid, [order.id], 'invoice')
			inv_ref.signal_workflow(cr, uid, [inv_id], 'invoice_open')

		
		for record in self.browse(cr, uid, ids, context=context):
			for st in record.statement_ids:
				if abs(st.difference) > st.journal_id.amount_authorized_diff:
					# The pos manager can close statements with maximums.
					if not self.pool.get('ir.model.access').check_groups(cr, uid, "point_of_sale.group_pos_manager"):
						raise osv.except_osv( _('Error!'),
							_("Your ending balance is too different from the theoretical cash closing (%.2f), the maximum allowed is: %.2f. You can contact your manager to force it.") % (st.difference, st.journal_id.amount_authorized_diff))
				if (st.journal_id.type not in ['bank', 'cash']):
					raise osv.except_osv(_('Error!'), 
						_("The type of the journal for your payment method should be bank or cash "))
				getattr(st, 'button_confirm_%s' % st.journal_id.type)(context=context)
		self._confirm_orders(cr, uid, ids, context=context)
		self.write(cr, uid, ids, {'state' : 'closed'}, context=context)

		obj = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'point_of_sale', 'menu_point_root')[1]
		return {
            'type' : 'ir.actions.client',
            'name' : 'Point of Sale Menu',
            'tag' : 'reload',
            'params' : {'menu_id': obj},
        }

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

class checador_registros(osv.osv):
	_name = 'consolidados.consolidado'
	_columns = {
			'fecha':fields.date('Fecha'),
			'horaEntrada':fields.datetime('Hora de Entrada'),
			'horaSalida': fields.datetime('Hora de Salida'),
			'usuario_id': fields.many2one('res.users','Usuario'),
	}
# class mamamia_checador(models.Model):
#     _name = 'mamamia_checador.mamamia_checador'

#     name = fields.Char()
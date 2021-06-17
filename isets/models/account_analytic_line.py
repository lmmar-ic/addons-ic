from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    iset_id = fields.Many2one('isets', store=True)
    iset_so_line_id = fields.Many2one('sale.order.line', store=True)
    sale_id = fields.Many2one('sale.order', store=True)
    type_id = fields.Many2one('working.type', 'Type', store=True)


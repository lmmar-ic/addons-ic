from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    work_base_id = fields.Many2one('work.base', store=True)
    work_base_so_line_id = fields.Many2one('sale.order.line', store=True)

    type_id = fields.Many2one('working.type', 'Type', store=True)
    sale_id = fields.Many2one('sale.order', 'Sale order', store=True)

# -*- coding: utf-8 -*-
##############################################################################
#    License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#    Copyright (C) 2021 Serincloud S.L. All Rights Reserved
#    Antonio Cánovas <antonio.canovas@ingenieriacloud.com>
#    Pedro josé Baños Guirao <pedro@serincloud.com>
##############################################################################
from odoo import api, fields, models, _


class RoiSet(models.Model):
    _name = "roi.set"
    _description = "ROI Set"

    name = fields.Char(string='Name')
    line_ids = fields.One2many(
        'roi.set.line',
        'set_id',
        string='Set line',
    )

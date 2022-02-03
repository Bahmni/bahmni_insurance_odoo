from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
import datetime 
import time
import calendar
import logging
_logger = logging.getLogger(__name__)


class account_invoice(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    @api.multi
    @api.onchange('amount')
    def onchange_sale_orders_add_claim(self):
        """
        Trigger the change of sale order to add claims for associated sale orders
        """
        _logger.info("onchange_sale_orders_add_claim") 
        paymentType = self.invoice_ids.payment_type
        wt = self.env['payment.journal.mapping']
        id_needed = wt.search([('payment_type', '=', paymentType)]).journal_id
        if id_needed:
            for payment in self:                
                payment.update({
                    'journal_id': id_needed
                })    
                payment.currency_id = payment.journal_id.currency_id or payment.company_id.currency_id
                # Set default payment method (we consider the first to be the default one)
                payment_methods = payment.payment_type == 'inbound' and payment.journal_id.inbound_payment_method_ids or payment.journal_id.outbound_payment_method_ids
                payment.payment_method_id = payment_methods and payment_methods[0] or False
                # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
                payment_type = payment.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
                return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}    


class account_invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH')], default='cash', string="Payment Type", required="True", help="Payment type accepted for this invoice", states={'draft': [('readonly', False)]})    
    amount_all_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_compute_all_amount', track_visibility='always')
    amount_all_total = fields.Monetary(string='Total',   store=True, readonly=True, compute='_compute_all_amount')
    claim_code=fields.Char(string='Claim Code', compute='_get_claim_code')
    nepali_date=fields.Char(string='Nepali Date', compute='_get_nepali_date')
    
    @api.one
    def _get_nepali_date(self):
        from datetime import datetime
        iyear = int(date.today().strftime('%Y'))
        imonth = int(date.today().strftime('%m'))
        iday = int(date.today().strftime('%d'))
        convertedDate=self.Adtobs(iyear,imonth,iday)
        self.update({
                    'nepali_date': convertedDate
                })
        self.nepali_date =convertedDate
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_all_amount(self):
        accountInvoice = self.env['account.invoice'].search([('origin', '=', self.origin)])
        for obj in accountInvoice:
            self.amount_all_untaxed = self.amount_all_untaxed +obj.amount_untaxed
            self.amount_all_total = self.amount_all_total +obj.amount_total

    
    def _get_claim_code(self):
        for accountInvoice in self:
            claim_code = "None"
            insuranceClaim = self.env['insurance.claim'].search([])
            for iclaim in insuranceClaim:
                for sorder in iclaim.sale_orders:
                    if sorder.name == accountInvoice.origin:
                        claim_code = iclaim.claim_code
            accountInvoice.claim_code = claim_code

    @api.multi
    def print_all_data(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'bahmni_insurance_odoo.report_invoice_combined')
    
    def Adtobs(self,engYear,engMonth,engDate):
        
        nepaliMonths = [
                    [ 30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31 ],  #2000
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],  #2001
                    [ 31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 30, 32, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 30, 32, 31, 32, 31, 31, 29, 30, 29, 30, 29, 31 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],  #2071
                    [ 31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],  #2072
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31 ],  #2073
                    [ 31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31 ],
                    [ 31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30 ],
                    [ 31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30 ],
                    [ 30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30 ],
                    [ 31, 32, 31, 32, 30, 31, 30, 30, 29, 30, 30, 30 ],
                    [ 30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 30, 29, 30, 30, 30 ],
                    [ 30, 31, 32, 32, 30, 31, 30, 30, 29, 30, 30, 30 ],
                    [ 30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30 ],
                    [ 30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30 ],  #2090
                    [ 31, 31, 32, 31, 31, 31, 30, 30, 29, 30, 30, 30 ],
                    [ 30, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30 ],
                    [ 30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 30, 30, 30, 30 ],
                    [ 30, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30 ],
                    [ 31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30 ],
                    [ 31, 31, 32, 31, 31, 31, 29, 30, 29, 30, 29, 31 ],
                    [ 31, 31, 32, 31, 31, 31, 30, 29, 29, 30, 30, 30 ]   #2099
                ]

        #engMonth, engDate, engYear = map(int, input("Enter English Month, Date and Year seperated by space: ").split())
        # engMonth=7
        # engDate=18 
        # engYear=2021


        #Define the least possible English date 1944/01/01 Saturday.

        startingEngYear = 1944
        startingEngMonth = 1
        startingEngDay = 1
        dayOfWeek = calendar.SATURDAY  


        #Let's define the equivalent Nepali date 2000/09/17.

        startingNepYear = 2000
        startingNepMonth = 9
        startingNepday = 17


        # Let's calculate the number of days between the two English dates as follows:

        date0=date(engYear,engMonth,engDate)
        date1=date(startingEngYear,startingEngMonth,startingEngDay)
        diff=(date0 - date1).days


        #Initialize required nepali date variables with starting  nepali date
        nepYear = startingNepYear
        nepMonth = startingNepMonth
        nepDay = startingNepday

        #Decreament delta.days until its value becomes zero.
        while diff != 0:

            # Getting total number of days in month nepMonth in a year nepYear
            daysInMonth = nepaliMonths[nepYear - 2000][nepMonth - 1]
            nepDay+=1 # incrementing nepali day

            if(nepDay > daysInMonth):
                nepMonth+=1
                nepDay = 1

            if(nepMonth > 12):
                nepYear+=1
                nepMonth = 1

            dayOfWeek+=1 
            #counting the days in terms of 7 days
            if(dayOfWeek > 7):
                dayOfWeek = 1

            diff-=1	
        # finally we print the converted date
        # print("Your equivalent Nepali date is: %s,%s,%s " %(nepYear, nepMonth, nepDay))
        # convertedBSDATE =str(nepYear) + "/"+str(nepMonth)+"/"+str(nepDay) 
        # raise UserError(convertedBSDATE)
        # return "2077-05-06"
        return str(nepYear) + "/"+str(nepMonth)+"/"+str(nepDay)

import pytz
from bs4 import BeautifulSoup
from odoo import fields, models,api

class Comment(models.Model):
    _name = "smart_office.comment"
    _description = "Comments of a noting"

    name = fields.Html('Comment')
    noting_id = fields.Many2one("smart_office.noting","Noting",required=True)
    state = fields.Selection(selection=[('draft','Draft'),('submitted','Submitted')],string="Status",required=True,default="draft")
    employee_id = fields.Many2one("hr.employee","Employee")
    job_id = fields.Many2one("hr.job","Designation")
    job_post_id = fields.Many2one('stpi.job.post', 'Functional Designation')
    branch_id = fields.Many2one("res.branch","Center")
    department_id = fields.Many2one("hr.department","Department")
    secondary_employee_ids = fields.Many2many("hr.employee",string="Secondary Owners")
    forward_date = fields.Date("Forward Date")
    forward_time = fields.Datetime("Forwarded On")
    # used for string extraction from html
    plain_text = fields.Text("Plain Text")
    is_extracted = fields.Boolean("Extracted ?",help="Becomes true once extraction is completed.")
    # index_id = fields.Integer("Lucene Index Doc ID")
    is_indexed = fields.Boolean("Indexed ?",help="Becomes true once indexing is completed.")


    @api.model
    def create(self, vals):
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        if employee:
            vals['employee_id'] = employee.id
            vals['secondary_employee_ids'] = [[4,employee.id]]
            vals['job_id'] = employee.job_id.id
            vals['job_post_id'] = employee.job_title.id
            vals['branch_id'] = employee.branch_id.id
            vals['department_id'] = employee.department_id.id
        return super(Comment, self).create(vals)

    def get_user_timezone_time(self):
        self.ensure_one()
        user_tz = self.env.user.tz or 'UTC'
        local = pytz.timezone(user_tz)
        return self.forward_time.astimezone(local).strftime('%d/%m/%Y %H:%M %p')

class Noting(models.Model):
    _name = 'smart_office.noting'
    _description = 'Noting'
    _rec_name = 'subject'

    folder_id = fields.Many2one('folder.master','File')
    content = fields.Html('Content')
    subject = fields.Char("Subject",required=False)
    # correspondence_ids = fields.One2many('muk_dms.file','noting_id','Correspondences')
    state = fields.Selection(selection=[('draft','Draft'),('submitted','Submitted')],string="Status",required=True,default="draft")
    comment_ids = fields.One2many('smart_office.comment', 'noting_id',string="Comments",domain=lambda self:[('state','=','submitted'),('secondary_employee_ids','in',self.env.user.employee_ids.ids)])
    
    employee_id = fields.Many2one("hr.employee","Employee")
    job_id = fields.Many2one("hr.job","Designation")
    job_post_id = fields.Many2one('stpi.job.post', 'Functional Designation')
    branch_id = fields.Many2one("res.branch","Center")
    department_id = fields.Many2one("hr.department","Department")
    forward_date = fields.Date("Forward Date")
    forward_time = fields.Datetime("Forwarded On")

    secondary_employee_ids = fields.Many2many("hr.employee",string="Secondary Owners")
    sequence = fields.Char("Sequence")
    is_last_sequence = fields.Boolean("Last Sequence ?",compute="_compute_if_last_sequence")

    # used for string extraction from html
    plain_text = fields.Text("Plain Text")
    is_extracted = fields.Boolean("Extracted ?",help="Becomes true once extraction is completed.")
    # index_id = fields.Integer("Lucene Index Doc ID")
    is_indexed = fields.Boolean("Indexed ?",help="Becomes true once indexing is completed.")

    @api.model
    def extract_text_from_noting_comment(self):
        # print("scheduler called")
        submitted_notings = self.search([('content','!=',False),('state','=','submitted'),('is_extracted','=',False)])
        submitted_comments = self.comment_ids.search([('name','!=',False),('state','=','submitted'),('is_extracted','=',False)])
        # print("both datas",submitted_notings,submitted_comments)
        for noting in submitted_notings:
            soup = BeautifulSoup(noting.content, features="html.parser")
            for script in soup(["script", "style"]):
                script.extract()
            extracted_text = ' '.join(soup.get_text().split())
            noting.write({'plain_text':extracted_text,'is_extracted':True})
        # process and extract text from comments
        for comment in submitted_comments:
            soup = BeautifulSoup(comment.name, features="html.parser")
            for script in soup(["script", "style"]):
                script.extract()
            extracted_text = ' '.join(soup.get_text().split())
            comment.write({'plain_text':extracted_text,'is_extracted':True})

        unindexed_notings = self.search([('plain_text','!=',False),('is_indexed','=',False),('is_extracted','=',True)])
        unindexed_comments = self.comment_ids.search([('plain_text','!=',False),('is_indexed','=',False),('is_extracted','=',True)])
        if unindexed_notings or unindexed_comments:
            try:
                print("Processing indexing with lucene...")
                import lucene
                from java.util import Arrays
                from java.nio.file import Paths

                from org.apache.lucene.analysis import CharArraySet
                from org.apache.lucene.analysis.standard import StandardAnalyzer
                from org.apache.lucene.analysis.en import EnglishAnalyzer
                from org.apache.lucene.analysis.hi import HindiAnalyzer
                from org.apache.lucene.document import Document,Field
                from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
                from org.apache.lucene.document import Document, Field,TextField
                from org.apache.lucene.index import  IndexWriter, IndexWriterConfig, DirectoryReader
                from org.apache.lucene.store import SimpleFSDirectory

                vm_env = lucene.getVMEnv()
                if not vm_env:
                    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
                else:
                    # vm_env = lucene.getVMEnv()
                    vm_env.attachCurrentThread()

                index_directory = self.env.ref('smart_office.smart_office_lucene_index_directory').value
                # print("indexing system parameter--->",index_directory)

                store = SimpleFSDirectory(Paths.get(index_directory))
                writer = None
                # try:
                hindi_stop_words = list(HindiAnalyzer().getStopwordSet())
                english_stop_words = list(EnglishAnalyzer.ENGLISH_STOP_WORDS_SET)

                stopWords = Arrays.asList(hindi_stop_words + english_stop_words)
                custom_stop_set =  CharArraySet(stopWords, True)

                analyzer = StandardAnalyzer(custom_stop_set)
                analyzer = LimitTokenCountAnalyzer(analyzer, 10000)
                config = IndexWriterConfig(analyzer)

                config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
                # config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)

                writer = IndexWriter(store, config)
                index_reader = DirectoryReader.open(writer)
                # total_docs = index_reader.numDocs()
                # updated_count = 0
                # print("Initially count of documents....",total_docs)
                if unindexed_notings:
                    print(f"indexing {len(unindexed_notings)} notings with lucene.....")
                    for noting in unindexed_notings:
                        note_subject = noting.subject and f' {noting.subject}' or ''
                        doc = Document()
                        doc.add(Field("data", noting.plain_text + note_subject, TextField.TYPE_STORED))
                        doc.add(Field("note_id", noting.id, TextField.TYPE_STORED))
                        writer.addDocument(doc)
                        # updated_count = index + total_docs
                        # noting.index_id = updated_count
                        noting.is_indexed = True

                if unindexed_comments:
                    print(f"indexing {len(unindexed_comments)} comments with lucene.....")
                    # updated_count += 1
                    for comment in unindexed_comments:
                        doc = Document()
                        doc.add(Field("data", comment.plain_text, TextField.TYPE_STORED))
                        doc.add(Field("comment_id", comment.id, TextField.TYPE_STORED))
                        writer.addDocument(doc)
                        # comment.index_id = index + updated_count
                        comment.is_indexed = True

                index_reader = DirectoryReader.open(writer)
                total_docs = index_reader.numDocs()
                print("total  docs after processing comments---->",total_docs)
                # finally:
                writer.close()
                store.close()

            except Exception as e:
                print("exception is---->",e)

    @api.multi
    def _compute_if_last_sequence(self):
        file_notings = self.search([('folder_id','in',self.mapped('folder_id').ids),('state','=','submitted')])
        for noting in self.filtered(lambda r:r.state =='submitted'):
            related_file_notings = file_notings.filtered(lambda r: r.folder_id == noting.folder_id)
            max_sequence = max(related_file_notings.mapped(lambda r:int(r.sequence)))
            if int(noting.sequence) == max_sequence:
                noting.is_last_sequence = True

    @api.model
    def create(self, vals):
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        if employee:
            vals['employee_id'] = employee.id
            vals['secondary_employee_ids'] = [[4,employee.id]]
            vals['job_id'] = employee.job_id.id
            vals['job_post_id'] = employee.job_title.id
            vals['branch_id'] = employee.branch_id.id
            vals['department_id'] = employee.department_id.id
        vals['sequence'] = self.env['ir.sequence'].next_by_code('smart_office_noting_sequence')
        return super(Noting, self).create(vals)

    def get_user_timezone_time(self):
        self.ensure_one()
        user_tz = self.env.user.tz or 'UTC'
        local = pytz.timezone(user_tz)
        return self.forward_time.astimezone(local).strftime('%d/%m/%Y %H:%M %p')
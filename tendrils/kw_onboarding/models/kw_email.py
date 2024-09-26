from odoo import models, fields, api, exceptions
import smtplib
import ssl


class send_email(models.Model):
    _name = 'send_email'
    _description = "A  model to send emails."

    email_id = fields.Char()

    # A method to send mail : Opening
    @api.multi
    def send_mail(self, vals):
        email_id = vals['mail_id']
        otp = vals['message']
        emailid = "recipient@example.com"  
        # print(otp)
        smtp_server = "mail.csmpl.com"
        port = 25  # For starttls
        sender_email = "asish.nayak@csmpl.com"
        password = "csmpl#6856"
        # Create a secure SSL context
        context = ssl.create_default_context()
        sender_email = "asish.nayak@csmpl.com"
        receiver_email = emailid
        SUBJECT = "CSM Enrollment Process"
        text = otp
        BODY = "\r\n".join((
            "From: %s" % sender_email,
            "To: %s" % receiver_email,
            "Subject: %s" % SUBJECT,
            "",
            text
        ))
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.ehlo()  # Can be omitted
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, BODY)
        except Exception as e:
            # print(e)
            pass
        finally:
            server.quit()

    # A method to send mail : Ending

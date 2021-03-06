import datetime
import os
import smtplib
import socket

import king_phisher.plugins as plugin_opts
import king_phisher.server.plugins as plugins
import king_phisher.server.signals as signals
import king_phisher.templates

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EXAMPLE_CONFIG = """
  smtp_server: <smtp.server.com>
  smtp_port: <port>
  smtp_email: <source_email>
  smtp_username: <username>
  smtp_password: <password>
  smtp_ssl: <boolean>
  email_jinja_template: <path>
"""

HTML_EMAIL_TEMPLATE = """
<class=MsoNormal><o:p>&nbsp;</o:p></p><table class=MsoNormalTable border=0 cellspacing=0 cellpadding=0 width="100%" 
style='width:100.0%;background:#00203a'><tr><td style='padding:15.0pt 0in 15.0pt 0in'><div align=center>
<table class=MsoNormalTable border=0 cellspacing=0 cellpadding=0 width="95%" style='width:95.0%'><tr><td 
style='padding:7.5pt 0in 15.0pt 0in'><table class=MsoNormalTable border=1 cellspacing=0 cellpadding=0 width="100%" 
style='width:100.0%;background:#5d84a8;border:solid #FFC20E 1.0pt;border-top:solid #FFC20E 3.0pt'><tr>
<td style='border:none;padding:.15in .15in .15in .15in'><table class=MsoNormalTable border=0 cellspacing=3 cellpadding=0 width="100%" 
style='width:100.0%'><tr><td style='padding:.75pt .75pt .75pt .75pt'><h1 align=center style='text-align:center'><span 
style='color:white;font-size:19.5pt;font-weight:normal'>King Phisher Campaign Alert Triggered<o:p></o:p></span></h1>
<table class=MsoNormalTable border=0 cellspacing=3 cellpadding=0 width="100%" style='width:100.0%;background:#FFC20E'>
<tr><td style='padding:3.0pt 3.0pt 3.0pt 3.0pt'><p class=MsoNormal align=center style='margin-bottom:15.0pt;text-align:center'>
<span style='color:black;text-transform:uppercase;letter-spacing:1.2pt'>Status update for: {{ campaign.name }} <o:p>
</o:p></span></p></td></tr></table></td></tr><tr><td style='padding:.75pt .75pt .75pt .75pt'><table class=MsoNormalTable 
border=0 cellspacing=3 cellpadding=0 width="100%" style='width:100.0%'><tr><td style='color:white;padding:.75pt .75pt .75pt 
.75pt'><h2><span style='font-size:13.5pt'>Basic Details:<o:p></o:p></span></h2></td></tr><tr><td style='padding:.75pt 
.75pt .75pt .75pt;_border: none'><table class=MsoNormalTable border=1 cellspacing=0 cellpadding=0 width="100%" 
style='width:100.0%;border-collapse:collapse;border:none'><tr><td width=180 style='width:135.0pt;border:solid #414747 
1.0pt;background:#EEEEEE;padding:3.75pt 3.75pt 3.75pt 3.75pt'><p class=MsoNormal><b><span style='font-size:10.5pt'>
Campaign Name<o:p></o:p></span></b></p></td><td style='border:solid #414747 1.0pt;border-left:none;padding:3.75pt 
3.75pt 3.75pt 3.75pt;background:#EEEEEE'><p class=MsoNormal><code><span style='font-size:10.0pt'>{{ campaign.name }}
</span></code><span style='font-size:10.5pt'><o:p></o:p></span></p></td></tr><tr><td width=180 style='width:135.0pt;border:solid #414747 
1.0pt;border-top:none;background:#EEEEEE;padding:3.75pt 3.75pt 3.75pt 3.75pt;_border: none'><p class=MsoNormal><b><span 
style='font-size:10.5pt'>Number of Visitors<o:p></o:p></span></b></p></td><td style='border-top:none;border-left:none;
border-bottom:solid #414747 1.0pt;border-right:solid #414747 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt;background:#EEEEEE'>
<p class=MsoNormal><code><span style='font-size:10.0pt'>{{ campaign.visit_count }}</span></code><span style='font-size:10.5pt'>
<o:p></o:p></span></p></td></tr><div>{% if campaign.credential_count %}
	<tr>
	<td 
	width=180 style='width:135.0pt;border:solid #414747 
	1.0pt;border-top:none;background:#EEEEEE;padding:3.75pt 3.75pt 3.75pt 
	3.75pt;_border: none'><p class=MsoNormal><b><span 
	style='font-size:10.5pt'>Number of Credentials<o:p></o:p></span></b></p></td><td 
	style='border-top:none;border-left:none;border-bottom:solid #414747 
	1.0pt;border-right:solid #414747 1.0pt;padding:3.75pt 3.75pt 3.75pt 
	3.75pt;background:#EEEEEE'><p class=MsoNormal><code><span 
	style='font-size:10.0pt'>{{ campaign.credential_count }}</span></code><span 
	style='font-size:10.5pt'><o:p></o:p></span></p></td></tr>
{% endif %}
</div><tr><td width=180 style='width:135.0pt;border:solid #414747 1.0pt;border-top:none;background:#EEEEEE;padding:3.75pt 3.75pt 3.75pt 
3.75pt;_border: none'><p class=MsoNormal><b><span style='font-size:10.5pt'>Time Alert Triggered<o:p></o:p></span></b></p>
</td><td style='border-top:none;border-left:none;border-bottom:solid #414747 1.0pt;border-right:solid #414747 1.0pt;
padding:3.75pt 3.75pt 3.75pt 3.75pt;background:#EEEEEE'><p class=MsoNormal><code><span style='font-size:10.0pt'>
{{ time.utc | strftime('%Y-%m-%dT%H:%M:%S+00:00') }}</span></code><span style='font-size:10.5pt'><o:p></o:p></span></p></td></tr><tr><td width=180 
style='width:135.0pt;border:solid #414747 1.0pt;border-top:none;background:#EEEEEE;padding:3.75pt 3.75pt 3.75pt 3.75pt;_border: none'>
<p class=MsoNormal><b><span style='font-size:10.5pt'>Campaign Expiration<o:p></o:p></span></b></p></td>
<td style='border-top:none;border-left:none;border-bottom:solid #414747 
1.0pt;border-right:solid #FFC20E 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt;background:#EEEEEE'><p class=MsoNormal><code>
<span style='font-size:10.0pt'>{{ campaign.expiration }}</span></code><span style='font-size:10.5pt'><o:p></o:p>
</span></p></td></tr></table></td></tr><tr><td style='padding:.75pt .75pt .75pt .75pt'>   <tr>
<td width="100%" style='width:100.0%;border:none;padding:7.5pt .15in 7.5pt .15in;min-width: 315px;max-width: 660px'>
<div align=center><table class=MsoNormalTable border=0 cellspacing=3 cellpadding=0 width="100%" style='width:100.0%'><tr>
<td style='padding:.75pt .75pt .75pt .75pt;color:white'><p class=MsoNormal>Powered by: 
<a href="https://github.com/securestate/king-phisher">RSM US, LLP</a> 
<o:p></o:p></p></td></tr></table></div></td></tr></table><div class="Footer">
<img src="https://github.com/securestate/king-phisher/raw/master/data/king-phisher-logo.png">
</div>
<p class=MsoNormal><o:p>&nbsp;</o:p></p></div></body></html>
"""

class Plugin(plugins.ServerPlugin):
	authors = ['Austin DeFrancesco', 'Spencer McIntyre', 'Mike Stringer', 'Erik Daguerre']
	classifiers = ['Plugin :: Server :: Notifications :: Alerts']
	title = 'Campaign Alerts: via Python 3 SMTPLib'
	description = """
	Send campaign alerts via the SMTP Python 3 lib. This requires that users specify
	their email through the King Phisher client to subscribe to notifications.
	"""
	homepage = 'https://github.com/securestate/king-phisher-plugins'

	# Email accounts with 2FA, such as Gmail, will not work unless "less secure apps" are allowed
	# Reference: https://support.google.com/accounts/answer/60610255
	# Gmail and other providers require SSL on port 465, TLS will start with the activation of SSL
	options = [
		plugin_opts.OptionString(
			name='smtp_server',
			description='Location of SMTP server',
			default='localhost'
		),
		plugin_opts.OptionInteger(
			name='smtp_port',
			description='Port used for SMTP server',
			default=25
		),
		plugin_opts.OptionString(
			name='smtp_email',
			description='SMTP email address to send notifications from',
			default=''
		),
		plugin_opts.OptionString(
			name='smtp_username',
			description='Username to authenticate to the SMTP server with'
		),
		plugin_opts.OptionString(
			name='smtp_password',
			description='Password to authenticate to the SMTP server with',
			default=''
		),
		plugin_opts.OptionBoolean(
			name='smtp_ssl',
			description='Connect to the SMTP server with SSL',
			default=False
		),
		plugin_opts.OptionString(
			name='email_jinja_template',
			description='Custom email jinja template to use for alerts',
			default=''
		),
	]
	req_min_version = '1.10'
	def initialize(self):
		signals.campaign_alert.connect(self.on_campaign_alert)
		self.email_jinja_template = HTML_EMAIL_TEMPLATE
		if os.path.isfile(self.config['email_jinja_template']):
			with open(self.config['email_jinja_template'], 'r') as file_:
				self.email_jinja_template = file_.read()
		elif self.config['email_jinja_template']:
			self.logger.warning('invalid email template: ' + self.config['email_jinja_template'])
			return False
		self.render_template = king_phisher.templates.TemplateEnvironmentBase().from_string(self.email_jinja_template)
		return True

	def on_campaign_alert(self, table, alert_subscription, count):
		user = alert_subscription.user
		if not self.config['smtp_email']:
			self.logger.debug("user {0} has no email address specified, skipping SMTP alert".format(user.id))
			return False
		return self.send_message(table, alert_subscription, count)

	def get_template_vars(self, table, alert_subscription, count):
		campaign = alert_subscription.campaign
		template_vars = {
			'campaign': {
				'id': str(campaign.id),
				'name': campaign.name,
				'created': campaign.created,
				'expiration': campaign.expiration,
				'has_expired': campaign.has_expired,
				'message_count': len(campaign.messages),
				'visit_count': len(campaign.visits),
				'credential_count': len(campaign.credentials)
			},
			'time': {
				'local': datetime.datetime.now(),
				'utc': datetime.datetime.utcnow()
			}
		}
		return template_vars

	def create_message(self, table, alert_subscription, count):
		message = MIMEMultipart()
		message['Subject'] = "Campaign Event: {0}".format(alert_subscription.campaign.name)
		message['From'] = "<{0}>".format(self.config['smtp_email'])
		message['To'] = "<{0}>".format(alert_subscription.user.email_address)

		textual_message = MIMEMultipart('alternative')
		txt_content = "{0:,} {1} reached for campaign: {2}".format(count, table.replace('_', ' '), alert_subscription.campaign.name)
		plaintext_part = MIMEText(txt_content, 'plain')
		textual_message.attach(plaintext_part)

		try:
			rendered_email = self.render_template.render(self.get_template_vars(table, alert_subscription, count))
		except:
			self.logger.warning('failed to render email jinja template', exc_info=True)
			return False
		html_part = MIMEText(rendered_email, 'html')
		textual_message.attach(html_part)

		message.attach(textual_message)
		encoded_email = message.as_string()
		return encoded_email

	def send_message(self, table, alert_subscription, count):
		msg = self.create_message(table, alert_subscription, count)
		if not msg:
			return False

		if self.config['smtp_ssl']:
			SmtpClass = smtplib.SMTP_SSL
		else:
			SmtpClass = smtplib.SMTP
		try:
			server = SmtpClass(self.config['smtp_server'], self.config['smtp_port'], timeout=15)
			server.ehlo()
		except smtplib.SMTPException:
			self.logger.warning('received an SMTPException while connecting to the SMTP server', exc_info=True)
			return False
		except socket.error:
			self.logger.warning('received a socket.error while connecting to the SMTP server')
			return False

		if not self.config['smtp_ssl'] and 'starttls' in server.esmtp_features:
			self.logger.debug('target SMTP server supports the STARTTLS extension')
			try:
				server.starttls()
				server.ehlo()
			except smtplib.SMTPException:
				self.logger.warning('received an SMTPException wile negotiating STARTTLS with SMTP server', exc_info=True)
				return False

		if self.config['smtp_username']:
			try:
				server.login(self.config['smtp_username'], self.config['smtp_password'])
			except smtplib.SMTPNotSupportedError:
				self.logger.debug('SMTP server does not support authentication')
			except smtplib.SMTPException as error:
				self.logger.warning("received an {0} while authenticating to the SMTP server".format(error.__class__.__name__))
				server.quit()
				return False

		mail_options = ['SMTPUTF8'] if server.has_extn('SMTPUTF8') else []
		try:
			server.sendmail(self.config['smtp_email'], alert_subscription.user.email_address, msg, mail_options)
		except smtplib.SMTPException as error:
			self.logger.warning("received error {0} while sending mail".format(error.__class__.__name__))
			return False
		finally:
			server.quit()
		self.logger.info('successfully sent alert email')
		return True

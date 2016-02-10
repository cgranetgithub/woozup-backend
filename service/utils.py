# #import os
#
# #def image_path(instance, filename):
#     #filename_base, filename_ext = os.path.splitext(filename)
#     #return '%s/%d%s'%(instance.__class__.__name__,
#                          #instance.user.id, filename_ext.lower())
#
# from django.template.loader import render_to_string
# from django.core.mail import EmailMultiAlternatives, EmailMessage
# from django.template import TemplateDoesNotExist
# from django.conf import settings
#
# def render_mail(template_prefix, emails, context):
#     """
#     Renders an e-mail to `emails`.  `template_prefix` identifies the
#     e-mail that is to be sent, e.g. "event/email/email_confirmation"
#     """
#     subject = render_to_string('{0}_subject.txt'.format(template_prefix),
#                                context)
#     # remove superfluous line breaks
#     subject = " ".join(subject.splitlines()).strip()
#
#     bodies = {}
#     for ext in ['html', 'txt']:
#         try:
#             template_name = '{0}_message.{1}'.format(template_prefix, ext)
#             bodies[ext] = render_to_string(template_name,
#                                            context).strip()
#         except TemplateDoesNotExist:
#             if ext == 'txt' and not bodies:
#                 # We need at least one body
#                 raise
#     if 'txt' in bodies:
#         msg = EmailMultiAlternatives(subject,
#                                      bodies['txt'],
#                                      settings.DEFAULT_FROM_EMAIL,
#                                      [],     #to
#                                      emails) #bcc
#         if 'html' in bodies:
#             msg.attach_alternative(bodies['html'], 'text/html')
#     else:
#         msg = EmailMessage(subject,
#                            bodies['html'],
#                            settings.DEFAULT_FROM_EMAIL,
#                            [],     #to
#                            emails) #bcc
#         msg.content_subtype = 'html'  # Main content is now text/html
#     return msg
#
# def send_mail(template_prefix, emails, context):
#     msg = render_mail(template_prefix, emails, context)
#     msg.send()

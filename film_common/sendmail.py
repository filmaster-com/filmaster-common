from django.core.mail.backends.base import BaseEmailBackend
from subprocess import Popen, PIPE

class SendmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        for msg in email_messages:
            self._send(msg)
        return len(email_messages)

    def _send(self, msg):
        p = Popen(['/usr/sbin/sendmail', '-t'], stdin=PIPE)
        p.communicate(msg.message().as_string())


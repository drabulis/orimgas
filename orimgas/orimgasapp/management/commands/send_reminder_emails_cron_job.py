from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db.models import Q

from orimgasapp.models import User, UserInstructionSign

class Command(BaseCommand):
    help = 'Send reminder emails to users and supervisors.'

    def handle(self, *args, **options):
        # Send reminder emails to users
        self.send_user_reminder_emails()

        # Send reminder emails to supervisors
        self.send_supervisor_reminder_emails()

    def send_user_reminder_emails(self):
        users_with_status_0 = User.objects.filter(userinstructionsign__status=0).distinct()

        for user in users_with_status_0:
            # Send reminder email to the user
            subject = 'Priminimas: Turite neužbaigtų darbų'
            message = f'Gerbiamas {user.first_name},\n\nKviečiame prisijungti prie jūsų profilio, susipažinti su instrukcijomis.\nPrie profilio prisijungti galite čia: \nPrimename, kad prisijungimo vardas jūsų elektroninis paštas.\n\nPagarbiai,\n„Orimgas“ komanda'
            send_mail(subject, message, 'info@orimgas.online', [user.email])

    def send_supervisor_reminder_emails(self):
        supervisor_users = User.objects.filter(is_supervisor=True)

        for supervisor in supervisor_users:
            # Get the users under the supervision with status=0
            supervised_users = User.objects.filter(
                company=supervisor.company,
                userinstructionsign__status=0
            ).distinct()
            if supervised_users:
                # Send reminder email to the supervisor
                subject = 'Priminimas: Įmonės darbuotojai, nesusipažinę su instrukcijomis'
                message = f'Gerbiamas {supervisor.first_name},\n\nŠie jūsų įmonės darbuotojai, nesusipažinę su instrukcijom:\n'
                
                for user in supervised_users:
                    message += f'- {user.first_name} {user.last_name}\n'

                message += '\nUžtikrinkite, kad darbuotojai susipažintu su instrukcijom.\n\nPagarbiai,\n„Orimgas“ komanda'

                send_mail(subject, message, 'info@orimgas.online', [supervisor.email])

        self.stdout.write(self.style.SUCCESS('Reminder emails sent successfully.'))

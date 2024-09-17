from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db.models import Q
from datetime import datetime, timedelta

from orimgasapp.models import User, UserInstructionSign, MokymuPasirasymas, PriesgaisriniuPasirasymas, KituDocPasirasymas, AAPPasirasymas

class Command(BaseCommand):
    help = 'Send reminder emails to users and supervisors.'

    def handle(self, *args, **options):
        # Send reminder emails to users
        self.send_user_reminder_emails()

        # Send reminder emails to supervisors
        self.send_supervisor_reminder_emails()

    def send_user_reminder_emails(self):
        users_with_status_0 = User.objects.filter(Q(userinstructionsign__status=0) | Q(mokymupasirasymas__status=0) | Q(priesgaisriniupasirasymas__status=0) | Q(kitudocpasirasymas__status=0) | Q(civilinesaugapasirasymas__status=0) | Q(aappasirasymas__status=0)).distinct()

        for user in users_with_status_0:
            subject = 'Priminimas: Turite neužbaigtų darbų'
            message = f"""
        Gerbiamas(-a) {user.first_name}, 

        Kviečiame prisijungti prie jūsų profilio, susipažinti su instrukcijomis.
        Prie profilio prisijungti galite čia: https://orimgas.online 
        Primename, kad prisijungimo vardas jūsų elektroninis paštas.
        Slaptažodis yra jūsų gimimo data.
        Slaptažodio formatas: Metai-Mėnuo-Diena (Skaičiais)

        Pagarbiai,
        „Orimgas“ komanda

        Dear {user.first_name}, 

        We invite you to log in to your profile and familiarize yourself with the instructions.
        You can log in to your profile here: https://orimgas.online 
        Please note that your login username is your email address.
        Your password is your date of birth.
        Password format: Year-Month-Day (Numbers)

        Best regards,
        The „Orimgas“ Team

        Уважаемый(-ая) {user.first_name}, 

        Приглашаем вас подключиться к своему профилю и ознакомиться с инструкциями.
        Вы можете подключиться к профилю здесь: https://orimgas.online 
        Напоминаем, что логином является ваш адрес электронной почты.
        Пароль – год вашего рождения.
        Формат пароля: Год-Месяц-День (цифры)

        С уважением,
        Команда „Orimgas“"""
            send_mail(subject, message, 'info@orimgas.online', [user.email])

    def send_supervisor_reminder_emails(self):
        supervisor_users = User.objects.filter(is_supervisor=True)

        for supervisor in supervisor_users:
            # Calculate one month from now
            one_month_from_now = datetime.now() + timedelta(days=30)

            # Get the users under the supervision with status=0
            supervised_users = User.objects.filter(
                Q(userinstructionsign__status=0) | Q(mokymupasirasymas__status=0) | Q(priesgaisriniupasirasymas__status=0) | Q(kitudocpasirasymas__status=0) | Q(civilinesaugapasirasymas__status=0) | Q(aappasirasymas__status=0),
                company=supervisor.company,
            ).distinct()

            # Get the users under the supervision with sekanti_med_patikros_data < one month from now
            upcoming_medical_users = User.objects.filter(
                company=supervisor.company,
                sekanti_med_patikros_data__lt=one_month_from_now,
                sekanti_med_patikros_data__isnull=False
            ).distinct()
            
            if supervised_users or upcoming_medical_users:
                # Send reminder email to the supervisor
                subject = 'Priminimas: Įmonės darbuotojai, nesusipažinę su instrukcijomis'
                message = f'Gerbiamas {supervisor.first_name},\n\nŠie jūsų įmonės darbuotojai, nesusipažinę su instrukcijom:\n'
                
                for user in supervised_users:
                    message += f'- {user.first_name} {user.last_name}\n'

                if upcoming_medical_users:
                    message += '\nŠiems darbuotojams artėja medicininė patikra:\n'
                    for user in upcoming_medical_users:
                        message += f'- {user.first_name} {user.last_name} (Patikros data: {user.sekanti_med_patikros_data.strftime("%Y-%m-%d")})\n'

                message += '\nUžtikrinkite, kad darbuotojai susipažintu su instrukcijom ir atliktų medicininę patikrą laiku.\nPrie profilio prisijungti galite čia: https://orimgas.online/\n\nPagarbiai,\n„Orimgas“ komanda'

                send_mail(subject, message, 'info@orimgas.online', [supervisor.email])

        self.stdout.write(self.style.SUCCESS('Reminder emails sent successfully.'))
from django_cron import CronJobBase, Schedule
from django.core.management import call_command


class RecreateUserInstructionSignsWeeklyCronJob(CronJobBase):
    schedule = Schedule(run_every_mins=1)  # Run every Monday at 12:00

    code = 'orimgasapp.recreate_user_instruction_signs_weekly_cron_job'


    def do(self):
        call_command('recreate_user_instruction_signs_weekly_cron_job')



class SendReminderEmailsCronJob(CronJobBase):
    schedule = Schedule(run_every_mins=1)  # Run every Monday at 12:00

    code = 'orimgasapp.send_reminder_emails_cron_job'

    def do(self):
        call_command('send_reminder_emails_cron_job')



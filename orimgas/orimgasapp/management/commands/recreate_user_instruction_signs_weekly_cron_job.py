from django.core.management.base import BaseCommand
from accounts.models import User
from orimgasapp.models import UserInstructionSign, PriesgaisriniuPasirasymas, MokymuPasirasymas, CivilineSaugaPasirasymas
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Recreate UserInstructionSign instances for active users as needed'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Scanning and recreating UserInstructionSign instances...'))

        today = timezone.now().date()

        # Get active users
        active_users = User.objects.filter(is_active=True)

        for user in active_users:
            # Get all completed signs for the user
            completed_instruction_signs = UserInstructionSign.objects.filter(
                user=user,
                status=1
            ).order_by('instruction__name', '-next_sign')

            # Get all incomplete signs for the user
            incomplete_instruction_signs = UserInstructionSign.objects.filter(
                user=user,
                status=0
            )

            # Keep track of the instances with the furthest next_sign date for each unique name
            latest_instances = {}

            # List to store signs to recreate
            signs_to_recreate = []

            # Iterate over completed signs
            for completed_sign in completed_instruction_signs:
                key = (completed_sign.instruction.name, completed_sign.instruction)
                if key not in latest_instances or completed_sign.next_sign > latest_instances[key].next_sign:
                    latest_instances[key] = completed_sign

            # Add the latest instances to the signs_to_recreate list
            signs_to_recreate.extend(latest_instances.values())

            # Filter out instances that are already in incomplete_signs
            signs_to_recreate = [sign for sign in signs_to_recreate if sign not in incomplete_instruction_signs]

            # Filter out instances that have an active instance with the same name and instruction
            signs_to_recreate = [sign for sign in signs_to_recreate if not incomplete_instruction_signs.filter(
                instruction=sign.instruction,
                status=0
            ).exists()]

            # Recreate the signs
            for sign_to_recreate in signs_to_recreate:
                # Calculate the difference in days between today and next_sign date
                days_until_next_sign = (sign_to_recreate.next_sign - today).days
                days_until_next_sign = max(0, days_until_next_sign)

                # Debug information
                self.stdout.write(self.style.SUCCESS(f'Days until next_sign for {sign_to_recreate.instruction.name}: {days_until_next_sign}'))

                # Check if today is 14 days or less from the next_sign date
                if days_until_next_sign <= 14:
                    # Debug information
                    self.stdout.write(self.style.SUCCESS(f'Recreating {sign_to_recreate.instruction.name} for user {sign_to_recreate.user}'))

                    # Recreate the specific instance
                    recreated_sign = sign_to_recreate.recreate_if_needed()

                    if recreated_sign:
                        self.stdout.write(self.style.SUCCESS(f'Recreated {sign_to_recreate.instruction.name} for user {sign_to_recreate.user}'))

            self.stdout.write(self.style.SUCCESS('Scanning and recreating PriesgaisriniuPasirasymas instances...'))

            completed_priesgaisrines_signs = PriesgaisriniuPasirasymas.objects.filter(
                user=user, status=1,).order_by('instruction__pavadinimas', '-next_sign')
            incomplete_priesgaisrines_signs = PriesgaisriniuPasirasymas.objects.filter(
                user=user, status=0)
            
            # Keep track of the instances with the furthest next_sign date for each unique name
            latest_priesgaisrines_instances = {}

            # List to store signs to recreate
            priesgaisrines_signs_to_recreate = []

            # Iterate over completed signs
            for completed_sign in completed_priesgaisrines_signs:
                key = (completed_sign.instruction.pavadinimas, completed_sign.instruction)
                if key not in latest_priesgaisrines_instances or completed_sign.next_sign > latest_priesgaisrines_instances[key].next_sign:
                    latest_priesgaisrines_instances[key] = completed_sign

            # Add the latest instances to the priesgaisrines_signs_to_recreate list
            priesgaisrines_signs_to_recreate.extend(latest_priesgaisrines_instances.values())

            # Filter out instances that are already in incomplete_signs
            priesgaisrines_signs_to_recreate = [sign for sign in priesgaisrines_signs_to_recreate if sign not in incomplete_priesgaisrines_signs]

            # Filter out instances that have an active instance with the same name and instruction

            priesgaisrines_signs_to_recreate = [sign for sign in priesgaisrines_signs_to_recreate if not incomplete_priesgaisrines_signs.filter(
                instruction=sign.instruction,
                status=0
            ).exists()]

            # Recreate the signs
            for sign_to_recreate in priesgaisrines_signs_to_recreate:
                # Calculate the difference in days between today and next_sign date
                days_until_next_sign = (sign_to_recreate.next_sign - today).days
                days_until_next_sign = max(0, days_until_next_sign)

                # Debug information
                self.stdout.write(self.style.SUCCESS(f'Days until next_sign for {sign_to_recreate.instruction.pavadinimas}: {days_until_next_sign}'))

                # Check if today is 14 days or less from the next_sign date
                if days_until_next_sign <= 14:
                    # Debug information
                    self.stdout.write(self.style.SUCCESS(f'Recreating {sign_to_recreate.instruction.pavadinimas} for user {sign_to_recreate.user}'))

                    # Recreate the specific instance
                    recreated_sign = sign_to_recreate.recreate_if_needed()

                    if recreated_sign:
                        self.stdout.write(self.style.SUCCESS(f'Recreated {sign_to_recreate.instruction.pavadinimas} for user {sign_to_recreate.user}'))

            self.stdout.write(self.style.SUCCESS('Scanning and recreating MokymuPasirasymas instances...'))

            completed_mokymu_signs = MokymuPasirasymas.objects.filter(
                user=user, status=1,).order_by('instruction__pavadinimas', '-next_sign')
            incomplete_mokymu_signs = MokymuPasirasymas.objects.filter(
                user=user, status=0)
            
            # Keep track of the instances with the furthest next_sign date for each unique name
            latest_mokymu_instances = {}

            # List to store signs to recreate
            mokymu_signs_to_recreate = []

            # Iterate over completed signs
            for completed_sign in completed_mokymu_signs:
                key = (completed_sign.instruction.pavadinimas, completed_sign.instruction)
                if key not in latest_mokymu_instances or completed_sign.next_sign > latest_mokymu_instances[key].next_sign:
                    latest_mokymu_instances[key] = completed_sign

            # Add the latest instances to the mokymu_signs_to_recreate list
            mokymu_signs_to_recreate.extend(latest_mokymu_instances.values())

            # Filter out instances that are already in incomplete_signs
            mokymu_signs_to_recreate = [sign for sign in mokymu_signs_to_recreate if sign not in incomplete_mokymu_signs]

            # Filter out instances that have an active instance with the same name and instruction

            mokymu_signs_to_recreate = [sign for sign in mokymu_signs_to_recreate if not incomplete_mokymu_signs.filter(
                instruction=sign.instruction,
                status=0
            ).exists()]

            # Recreate the signs
            for sign_to_recreate in mokymu_signs_to_recreate:
                # Calculate the difference in days between today and next_sign date
                days_until_next_sign = (sign_to_recreate.next_sign - today).days
                days_until_next_sign = max(0, days_until_next_sign)

                # Debug information
                self.stdout.write(self.style.SUCCESS(f'Days until next_sign for {sign_to_recreate.instruction.pavadinimas}: {days_until_next_sign}'))

                # Check if today is 14 days or less from the next_sign date
                if days_until_next_sign <= 14:
                    # Debug information
                    self.stdout.write(self.style.SUCCESS(f'Recreating {sign_to_recreate.instruction.pavadinimas} for user {sign_to_recreate.user}'))

                    # Recreate the specific instance
                    recreated_sign = sign_to_recreate.recreate_if_needed()

                    if recreated_sign:
                        self.stdout.write(self.style.SUCCESS(f'Recreated {sign_to_recreate.instruction.pavadinimas} for user {sign_to_recreate.user}'))
                        
            completed_civiline_signs = CivilineSaugaPasirasymas.objects.filter(
                user=user, status=1,).order_by('instruction__pavadinimas', '-next_sign')
            incomplete_civiline_signs = CivilineSaugaPasirasymas.objects.filter(
                user=user, status=0)
            
            # Keep track of the instances with the furthest next_sign date for each unique name
            latest_instances = {}

            # List to store signs to recreate
            signs_to_recreate = []

            # Iterate over completed signs
            for completed_sign in completed_civiline_signs:
                key = (completed_sign.instruction.pavadinimas, completed_sign.instruction)
                if key not in latest_instances or completed_sign.next_sign > latest_instances[key].next_sign:
                    latest_instances[key] = completed_sign

            # Add the latest instances to the signs_to_recreate list
            signs_to_recreate.extend(latest_instances.values())

            # Filter out instances that are already in incomplete_signs
            signs_to_recreate = [sign for sign in signs_to_recreate if sign not in incomplete_civiline_signs]

            # Filter out instances that have an active instance with the same name and instruction
            signs_to_recreate = [sign for sign in signs_to_recreate if not incomplete_civiline_signs.filter(
                instruction=sign.instruction,
                status=0
            ).exists()]

            # Recreate the signs
            for sign_to_recreate in signs_to_recreate:
                # Calculate the difference in days between today and next_sign date
                days_until_next_sign = (sign_to_recreate.next_sign - today).days
                days_until_next_sign = max(0, days_until_next_sign)

                # Debug information
                self.stdout.write(self.style.SUCCESS(f'Days until next_sign for {sign_to_recreate.instruction.pavadinimas}: {days_until_next_sign}'))

                # Check if today is 14 days or less from the next_sign date
                if days_until_next_sign <= 14:
                    # Debug information
                    self.stdout.write(self.style.SUCCESS(f'Recreating {sign_to_recreate.instruction.pavadinimas} for user {sign_to_recreate.user}'))

                    # Recreate the specific instance
                    recreated_sign = sign_to_recreate.recreate_if_needed()

                    if recreated_sign:
                        self.stdout.write(self.style.SUCCESS(f'Recreated {sign_to_recreate.instruction.pavadinimas} for user {sign_to_recreate.user}'))
# orimgasapp/management/commands/custom_makemessages.py
from django.core.management.commands import makemessages
from django.utils.translation import templatize
from collections import defaultdict
import os
import re

class Command(makemessages.Command):
    help = 'Extract translations without merging similar strings'

    def handle(self, *args, **options):
        # Disable fuzzy matching completely
        options['no_fuzzy'] = True
        
        # First run normal extraction to POT file
        super().handle(*args, **options)
        
        # Post-process the POT file
        self.clean_pot_file(options)

    def clean_pot_file(self, options):
        pot_path = os.path.join(options['locale'], 'django.pot')
        
        # Group messages by exact content
        messages = defaultdict(list)
        with open(pot_path, 'r', encoding='utf-8') as f:
            current_msg = []
            for line in f:
                if line.startswith('msgid '):
                    if current_msg:
                        msgid = current_msg[0].split('msgid ')[1].strip()
                        messages[msgid].append(current_msg)
                    current_msg = [line]
                elif current_msg:
                    current_msg.append(line)
        
        # Write back with exact matches merged
        with open(pot_path, 'w', encoding='utf-8') as f:
            for msgid, occurrences in messages.items():
                # Combine source references for identical strings
                all_sources = []
                for occurrence in occurrences:
                    sources = [l for l in occurrence if l.startswith('#: ')]
                    all_sources.extend(sources)
                
                # Write merged entry
                f.write('\n')
                f.writelines(all_sources)
                f.write(f'msgid {msgid}\n')
                f.write(f'msgstr ""\n')
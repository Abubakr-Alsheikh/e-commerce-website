import os
from django.conf import settings
from django.core.management.base import BaseCommand
import json
import ast  # Import 'ast' for safely evaluating lists

class Command(BaseCommand):
    help = 'Transforms a list from an input file to JSON and saves it to an output file'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str, help='Path to the input file containing the Python list')
        parser.add_argument('output_file', type=str, help='Path to the output JSON file')

    def handle(self, *args, **options):
        input_file = os.path.join(
            settings.MEDIA_ROOT, options['input_file']
        )
        output_file = os.path.join(
            settings.MEDIA_ROOT, options['output_file']
        )

        try:
            with open(input_file, 'r') as f:
                content = f.read()
                data = ast.literal_eval(content)  # Safely evaluate list from string

            output_json = []
            for item in data:
                if item.startswith("input:"):
                    output_json.append({
                        "role": "user",
                        "parts": [item.replace("input: ", "").strip()]
                    })
                elif item.startswith("output:"):
                    output_json.append({
                        "role": "model",
                        "parts": [item.replace("output: ", "").strip()]
                    })

            with open(output_file, 'w') as f:
                json.dump(output_json, f, indent=4)

            self.stdout.write(self.style.SUCCESS(f'Successfully converted list from {input_file} to JSON in {output_file}'))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'Input file "{input_file}" not found.'))
        except (SyntaxError, ValueError) as e:
            self.stderr.write(self.style.ERROR(f'Error reading list from input file: {e}. Ensure the file contains a valid Python list.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An error occurred: {e}'))
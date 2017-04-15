import os

from django.conf import settings
from django.core.management.base import BaseCommand

from monki.boards.models import Banner, Image, Video


class Command(BaseCommand):
    help = 'Clean media by deleting those files which are no more referenced by any FileField'

    def get_files_on_disk(self):
        files_on_disk = []

        for root, subdirs, files in os.walk(settings.MEDIA_ROOT):
            if 'CACHE' in subdirs:
                subdirs.remove('CACHE')

            for filename in files:
                root = root.replace(settings.MEDIA_ROOT + '/', '')

                filepath = os.path.join(root, filename)

                files_on_disk.append(filepath)

        return set(files_on_disk)

    def get_files_on_db(self):
        files_on_db = []

        for row in Banner.objects.all():
            files_on_db.append(row.image)

        for row in Image.objects.all():
            files_on_db.append(row.file)

        for row in Video.objects.all():
            files_on_db.append(row.file)
            files_on_db.append(row.image)

        return set(files_on_db)

    def handle(self, *args, **options):
        files_on_disk = self.get_files_on_disk()
        files_on_db = self.get_files_on_db()

        unused_files = files_on_disk - files_on_db

        self.stdout.write('[!] Files to delete: {}'.format(len(unused_files)))

        for unused_file in unused_files:
            os.unlink(settings.MEDIA_ROOT + '/' + unused_file)

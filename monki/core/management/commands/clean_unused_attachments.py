from django.core.management.base import BaseCommand

from monki.boards.models import Image, Video


class Command(BaseCommand):
    help = 'Clean ContentTypes which are no more referenced by any Post instance'

    def get_orphan_contenttype(self, model):
        orphans = []

        for row in model.objects.all():
            if row.post.count() == 0:
                orphans.append(row)

        return orphans

    def handle(self, *args, **options):
        orphans_images = self.get_orphan_contenttype(Image)
        orphans_videos = self.get_orphan_contenttype(Video)

        self.stdout.write('[!] Orphans Image to delete: {}'.format(len(orphans_images)))
        self.stdout.write('[!] Orphans Video to delete: {}'.format(len(orphans_videos)))

        for row in orphans_images + orphans_videos:
            row.delete()

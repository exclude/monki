from imagekit import ImageSpec, register
from imagekit.processors import ResizeToFit
from imagekit.utils import get_field_info


class Thumbnail(ImageSpec):
    format = 'JPEG'
    options = {'quality': 90}

    @property
    def processors(self):
        model, field_name = get_field_info(self.source)

        size = (225, 175)

        return [
            ResizeToFit(*size),
        ]


register.generator('boards:thumbnail', Thumbnail)

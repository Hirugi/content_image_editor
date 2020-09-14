from pathlib import Path

import numpy
from PIL import Image, ImageOps, ImageFile


class ImageProcessor:
    def process_image(self, image: Image, image_settings: dict, crop=True, square=True, opaque=True, fit=True,
                      **kwargs):
        # Flag for ignoring metadata of image, for ex. when it is
        # too large and cause PIL to raise exception
        ImageFile.LOAD_TRUNCATED_IMAGES = kwargs.get(
            'ignore_image_metadata', False)

        has_transparency = any(a in image.getbands() for a in ('a', 'A', 'P'))
        _color_limits = image_settings.get('color_limits')
        if _color_limits:
            color_limits = (
                _color_limits['red'], _color_limits['green'], _color_limits['blue'], _color_limits['alpha'])
        else:
            color_limits = (255, 255, 255, 0)

        im = image

        if crop:
            im = self._crop_to_actual_image(im, color_limits)

        if square:
            fill_color = (255, 255, 255)
            _fill_color = kwargs.get('square_fill_color')
            if _fill_color:
                fill_color = (
                    _fill_color['red'], _fill_color['green'], _fill_color['blue'])
            im = self._make_square_image(im, has_transparency, fill_color)

        if has_transparency and opaque:
            fill_color = (255, 255, 255)
            _fill_color = kwargs.get('opaque_fill_color')
            if _fill_color:
                fill_color = (
                    _fill_color['red'], _fill_color['green'], _fill_color['blue'])
            im = self._remove_transparency(im, fill_color)

        if fit:
            im = ImageOps.fit(
                im, (image_settings['width'], image_settings['height']), Image.ANTIALIAS)

        return im

    @staticmethod
    def _crop_to_actual_image(image: Image, color_limits=(252, 252, 252, 0)):
        """
        Crop image to actual image, oriented by set color limits
        :param image: Image object
        :param color_limits: Tuple for RBG color, image edges with colors above this limits
        will be cropped
        :return: Image object
        """
        # Convert image to RGBA mode because it can be in mode 'P' for example, which has only 1 band.
        _image = image.convert('RGBA')

        data = numpy.array(_image)
        red, green, blue, alpha = data.T

        white_areas = (
            ((red >= color_limits[0]) & (green >= color_limits[1]) & (blue >= color_limits[2])) |
            (alpha <= color_limits[3])
        )
        data[...,][white_areas.T] = (255, 255, 255, 0)

        _image = Image.fromarray(data)
        rgb_image = Image.new(
            mode='RGB', size=_image.size, color=(255, 255, 255))
        image_components = _image.split()
        rgb_image.paste(_image, mask=image_components[3])
        crop_box = _image.getbbox()
        return image.crop(crop_box)

    @staticmethod
    def _make_square_image(image: Image, has_alpha=False, fill_color=(255, 255, 255)):
        """
        Make a square image from input image
        :param image: Image object
        :param has_alpha: True if output image should have an alpha channel, else False
        :param fill_color: Tuple for RGB color to fill image borders
        :return: Image object
        """
        x, y = image.size
        size = max(x, y)
        # Add transparency level if has_alpha is True
        if has_alpha:
            fill_color = fill_color + (0,)
        square_image = Image.new(
            'RGBA' if has_alpha else 'RGB', (size, size), fill_color)
        square_image.paste(
            image,
            box=(int((size - x) / 2), int((size - y) / 2)))
        return square_image

    @staticmethod
    def _remove_transparency(image: Image, background_color=(255, 255, 255)):
        """
        Removes alpha channel from image
        :param image: Image object
        :param background_color: Tuple for RGB color
        :return: Image object
        """
        image.load()
        # Convert image to RGBA mode because it can be in mode 'P' for example, which has only 1 band.
        image = image.convert(mode='RGBA')
        image_with_background = Image.new('RGB', image.size, background_color)
        # Here, we need exactly 4 RGBA bands
        image_with_background.paste(image, mask=image.split()[3])
        return image_with_background


class ImageEditor(ImageProcessor):
    def __init__(self, image_name: str, in_dir: str, out_dir: str, image_settings: dict, **kwargs):
        image = Image.open(f'{in_dir}/{image_name}')
        image_format = Path(image_name).suffix
        opaque = kwargs.get('opaque')
        if kwargs.get('simple_formats'):
            if (any(a in image.getbands() for a in ('a', 'A', 'P'))) and not opaque:
                image_format = '.png'
            else:
                image_format = '.jpg'
        out_file_path = f'{out_dir}/{Path(image_name).stem}{image_format}'
        if kwargs.get('no_rewrite'):
            out_file_path = self._get_safe_path(out_file_path)

        image = self.process_image(image, image_settings, **kwargs)
        image.save(out_file_path, quality=image_settings.get('quality', 75))

    @staticmethod
    def _get_safe_path(path):
        full_file_path = path
        for i in range(10):
            # Add name_extension to file name and check new path is vacant
            full_file_path = Path(path)
            if not full_file_path.exists():
                return str(full_file_path)
            path = f'{full_file_path.parent}/{full_file_path.stem}_copy{full_file_path.suffix}'
        raise Exception(f'Too many copies in the folder, can not save file: {full_file_path}')


class EditorManager:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        ImageEditor(*self.args, **self.kwargs)

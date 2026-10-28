import numpy as np
from PIL import Image as pil

from core.services.global_logger import logFunc


class PixelComparisonDetector:
    """Find full-width white or black gutters, keeping uncertain areas intact."""

    @logFunc(inclass=True)
    def run(self, combined_img: pil.Image, split_height: int, **kwargs) -> list[int]:
        if split_height <= 0:
            raise ValueError('Panel height must be greater than zero')
        # Examine every pixel: ignoring edges can cut through a balloon or artwork.
        pixels = np.asarray(combined_img.convert('RGB'))
        height = pixels.shape[0]
        # Small tolerance accommodates JPEG artifacts, without accepting grey art.
        white = np.all(pixels >= 245, axis=(1, 2))
        black = np.all(pixels <= 10, axis=(1, 2))
        safe = white | black
        # A band, rather than a single empty row, avoids gaps between text lines.
        # Changing white to black does not form one continuous empty band.
        min_band = 24
        cuts = [0]
        start = 0
        bands = []
        while start < height:
            if not safe[start]:
                start += 1
                continue
            color = white[start]
            end = start + 1
            while end < height and safe[end] and white[end] == color:
                end += 1
            if end - start >= min_band:
                bands.append((start, end))
            start = end

        max_height = kwargs.get('max_height')
        while height - cuts[-1] > split_height or (
            max_height and height - cuts[-1] > max_height
        ):
            target = cuts[-1] + split_height
            maximum = min(height - 1, cuts[-1] + max_height) if max_height else height - 1
            minimum = cuts[-1] + max(1, int(split_height * 0.4))

            def find_candidates(lower):
                result = []
                for lo, hi in bands:
                    left = max(lo + min_band // 2, lower)
                    right = min(hi - min_band // 2, maximum)
                    if left <= right:
                        result.append(min(max(target, left), right))
                return result

            candidates = find_candidates(minimum)
            if not candidates and max_height and height - cuts[-1] > max_height:
                # A smaller page is preferable to splitting a balloon.
                candidates = find_candidates(cuts[-1] + 1)
            if not candidates:
                if max_height and height - cuts[-1] > max_height:
                    cut = maximum
                    forced = kwargs.get('forced_cuts')
                    if forced is not None:
                        forced.append(cut)
                    cuts.append(cut)
                    continue
                break
            cut = min(candidates, key=lambda y: (abs(y - target), y))
            cuts.append(cut)
        if cuts[-1] != height:
            cuts.append(height)
        return cuts

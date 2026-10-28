class DirectoryException(Exception):
    pass


class ProfileException(Exception):
    pass


class WebPSizeError(Exception):
    """A lossless safe cut cannot satisfy the WebP dimension limit."""
    pass

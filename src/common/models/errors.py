class RGError(Exception):
    """
    RG error
    """
    pass


class RGTemplateNotFoundError(RGError):
    """
    RG template not found error
    """
    pass


class RGInvalidConfigurationError(RGError):
    """
    RG invalid configuration error
    """
    pass


class RGUIError(RGError):
    """
    RG UI error
    """
    pass


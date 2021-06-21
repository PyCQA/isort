from natsort import natsorted


def natural_plus(*args, **kwargs) -> str:
    """An even more natural sorting order for isort using natsort."""
    return natsorted(*args, **kwargs)

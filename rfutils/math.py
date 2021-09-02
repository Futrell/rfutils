def linear_scale(x, old_min, old_max, new_min, new_max):
    unit = (x - old_min) / (old_max - old_min)
    return unit * (new_max - new_min) + new_min

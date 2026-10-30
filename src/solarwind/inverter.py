"""Inverter sizing."""

STANDARD_SIZES_KVA = [0.5, 1, 1.5, 2, 3, 3.5, 5, 6, 8, 10, 12, 15]


def required_kva(peak_watts, power_factor=0.8, headroom=1.25):
    """Inverter rating needed for a peak load, with headroom for start-up surges."""
    if not 0 < power_factor <= 1:
        raise ValueError("Power factor must be between 0 and 1")
    return peak_watts * headroom / power_factor / 1000


def standard_inverter_kva(needed_kva):
    """Smallest common inverter size that covers the requirement, or None if none is big enough."""
    for size in STANDARD_SIZES_KVA:
        if size >= needed_kva:
            return size
    return None

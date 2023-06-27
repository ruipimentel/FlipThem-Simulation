def milliseconds_to_timestring(milliseconds, show_ms=False):
    milliseconds = int(milliseconds)
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    time_string = f"{hours:02}:{minutes:02}:{seconds:02}{f'.{milliseconds:03}' if show_ms else ''}"
    return time_string

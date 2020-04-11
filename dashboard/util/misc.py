from datetime import timedelta


def duration_to_min_and_sec(duration: timedelta):
    total_secs = duration.total_seconds()
    minutes = int(total_secs // 60)
    seconds = int(total_secs % 60)
    return f'{str(minutes).zfill(2)}:{str(seconds).zfill(2)}'

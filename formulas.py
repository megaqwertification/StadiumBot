from math import floor, log2

# TODO: make these python 3 function style definitions
# TODO: Verify these formulas
def ft_to_m(score_ft) -> float:
    # https://docs.google.com/spreadsheets/d/11K1QI_sZi8ePWvejQAG-2uhvBEi7zTdBluscIFPl6Ow/edit#gid=0
    # using feet to metres column N
    conversion_factor = 0.304787998199462
    score_m = round(score_ft*conversion_factor ,1)
    return score_m

def m_to_ft(score_m) -> float:
    # using metres to feet column G
    conversion_factor = 30.4787998199462
    score = score_m * 100
    interim_1 = score/conversion_factor
    interim_2 = round(pow(2, 23 - floor(log2(interim_1))) * interim_1)/pow(2, 23 - floor(log2(interim_1)))
    score_feet = floor(round(pow(2, 23 - floor(log2(interim_2*10))) * interim_2*10)/pow(2, 23 - floor(log2(interim_2*10))))/10
  
    return score_feet


# time to frames
def time_to_frames(time: float) -> str:
    # should work for debug as well.
    return str(round(time*60))


# TODO: frames to time
# https://github.com/mchen91/mismatch-bot/blob/main/use_cases/frame_conversion.py
def frames_to_time_string(frames: int) -> str:
    hours, rem = divmod(frames, 60 * 60 * 60)
    minutes, rem = divmod(rem, 60 * 60)
    seconds, rem = divmod(rem, 60)
    centiseconds = (rem * 99) // 59
    padded_centis = str(centiseconds).zfill(2)
    if hours > 0:
        padded_minutes = str(minutes).zfill(2)
        padded_seconds = str(seconds).zfill(2)
        return f"{hours}:{padded_minutes}:{padded_seconds}.{padded_centis}"
    if minutes > 0:
        padded_seconds = str(seconds).zfill(2)
        return f"{minutes}:{padded_seconds}.{padded_centis}"
    return f"{seconds}.{padded_centis}"
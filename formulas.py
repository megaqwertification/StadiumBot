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
def time_to_frames(time):
    # should work for debug as well.
    return str(round(time*60))


# TODO: frames to time
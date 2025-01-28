from scipy.optimize import linear_sum_assignment

# from commands.btt_commands import _btt_wr_list
from constants.btt_constants import BTT_CHARACTERS, BTT_CHARS_STAGE_COMMAND, BTT_STAGES
# from .. import constants
from constants.general_constants import ALIASES
from formulas import get_char_name, time_to_frames, frames_to_time_string
from db import connect

from helper_functions.btt_helper_functions import filter_btt_tags, btt_wr_list


# TODO: Save results to a file rather than polling each time
# Or optimized DB query
# And cleanup the file structure a little more (see if you can get imports working when this file is under helper_scripts)

# DEBUG:
RTA_TIMES_MATRIX_TEST = [[13.11, 8.95, 2.6, 7.62, 8.65, 8.63, 8.11, 8.58, 3.7, 7.46, 11.5, 10.82, 11.87, 9.93, 8.58, 6.2, 7.08, 'inf', 7.33, 9.99, 12.92, 4.01, 2.67, 8.82, 6.08], [11.52, 7.87, 2.72, 6.48, 8.38, 7.93, 7.7, 8.1, 3.62, 7.0, 9.97, 9.85, 10.99, 8.95, 8.35, 5.35, 6.67, 8.65, 6.38, 9.95, 10.15, 4.4, 2.78, 7.78, 5.72], [12.75, 10.95, 3.0, 7.97, 9.97, 9.87, 8.15, 8.73, 3.72, 7.75, 10.18, 11.4, 11.35, 11.85, 10.6, 9.63, 7.63, 'inf', 8.78, 12.11, 9.36, 4.97, 2.82, 10.73, 
6.88], [17.08, 11.11, 2.85, 8.06, 10.45, 'inf', 9.45, 9.99, 4.68, 7.88, 13.8, 14.33, 14.1, 11.21, 10.68, 9.9, 7.9, 'inf', 7.7, 11.25, 'inf', 5.03, 2.99, 11.25, 6.87], [12.93, 10.28, 2.9, 8.57, 8.93, 8.85, 8.35, 9.99, 3.78, 6.72, 8.4, 12.48, 12.28, 10.52, 7.5, 5.88, 6.8, 13.16, 7.01, 11.0, 8.95, 5.55, 2.82, 9.58, 6.26], [10.95, 9.2, 2.72, 8.05, 8.55, 6.92, 7.97, 8.6, 3.99, 6.73, 10.95, 10.99, 12.0, 9.13, 8.77, 5.92, 7.75, 'inf', 6.75, 9.83, 'inf', 5.31, 2.75, 9.1, 5.99], [15.82, 11.13, 3.6, 7.95, 9.97, 'inf', 8.33, 9.99, 4.0, 8.55, 12.52, 13.15, 11.87, 10.85, 9.55, 10.11, 6.82, 'inf', 6.63, 10.03, 13.16, 5.43, 2.75, 10.57, 6.05], [12.58, 9.25, 2.95, 6.85, 7.99, 8.18, 6.3, 7.25, 3.87, 7.06, 8.43, 11.31, 9.63, 9.23, 7.31, 8.03, 5.9, 10.35, 5.99, 9.31, 'inf', 4.95, 2.18, 8.52, 5.36], ['inf', 12.65, 3.99, 9.16, 13.8, 9.77, 9.99, 11.36, 4.43, 9.3, 12.45, 16.73, 13.5, 12.72, 10.57, 10.95, 9.9, 'inf', 8.65, 12.08, 'inf', 5.99, 2.62, 11.11, 7.31], [7.82, 5.67, 2.2, 6.31, 6.58, 5.53, 4.46, 4.26, 3.73, 4.53, 6.48, 9.26, 6.52, 8.57, 6.8, 6.16, 4.58, 'inf', 4.85, 7.58, 5.88, 3.95, 1.73, 7.63, 4.53], [7.63, 5.77, 1.46, 5.88, 5.97, 5.58, 3.57, 4.23, 3.67, 
5.21, 6.38, 9.41, 6.38, 8.6, 6.95, 6.57, 3.78, 'inf', 4.87, 6.68, 4.92, 3.67, 1.57, 6.87, 4.93], [16.46, 10.77, 2.99, 7.87, 9.33, 9.26, 9.1, 10.87, 4.46, 6.65, 11.99, 12.95, 13.55, 10.73, 9.92, 6.99, 8.21, 'inf', 7.73, 12.4, 13.93, 6.33, 2.8, 10.87, 7.28], [16.48, 9.82, 3.2, 9.92, 11.4, 'inf', 8.31, 10.73, 4.73, 8.11, 12.72, 14.4, 9.7, 11.46, 9.18, 7.97, 7.92, 'inf', 8.7, 11.78, 'inf', 5.5, 2.77, 8.1, 7.01], [17.57, 12.41, 3.93, 9.62, 10.4, 10.97, 9.5, 11.35, 
3.9, 7.36, 10.82, 14.97, 14.2, 11.46, 11.48, 9.67, 8.35, 'inf', 8.53, 13.36, 10.75, 6.67, 3.3, 12.05, 6.93], [8.82, 7.25, 2.78, 7.23, 6.95, 6.82, 7.1, 8.1, 3.55, 6.7, 7.97, 9.93, 8.33, 9.97, 7.53, 5.08, 5.23, 9.9, 6.53, 9.36, 8.23, 4.35, 1.93, 8.57, 5.68], [13.8, 8.65, 2.88, 7.85, 7.73, 7.77, 7.95, 9.48, 3.87, 7.33, 8.58, 11.88, 8.63, 9.68, 8.99, 5.97, 6.55, 11.55, 7.26, 9.88, 15.33, 4.72, 2.55, 7.93, 6.35], [6.93, 5.18, 2.15, 4.28, 4.13, 4.95, 5.45, 4.92, 3.23, 3.46, 4.87, 5.87, 7.53, 4.25, 4.08, 4.25, 3.48, 8.26, 4.0, 5.31, 4.36, 3.77, 1.87, 4.9, 4.68], [6.73, 4.53, 2.11, 4.25, 4.58, 4.67, 4.78, 4.99, 3.1, 3.63, 5.85, 5.48, 6.48, 3.99, 4.25, 3.93, 3.63, 4.8, 3.88, 4.78, 3.88, 3.05, 1.83, 4.88, 4.77], [11.97, 7.75, 2.85, 7.36, 6.18, 6.82, 7.63, 7.33, 3.46, 5.73, 7.7, 9.87, 9.93, 6.48, 6.55, 5.06, 6.77, 9.78, 5.45, 7.95, 13.93, 4.15, 2.62, 8.85, 6.01], [10.01, 7.53, 2.1, 7.08, 6.15, 6.77, 6.99, 6.57, 3.48, 5.65, 6.73, 9.16, 9.4, 6.06, 6.36, 5.21, 5.75, 'inf', 5.45, 6.8, 8.82, 4.13, 2.05, 7.93, 5.28], [15.88, 11.82, 3.55, 9.28, 10.7, 10.82, 9.63, 11.58, 4.18, 8.33, 11.77, 16.21, 15.38, 10.78, 10.25, 8.87, 7.11, 16.62, 8.7, 13.6, 7.33, 6.06, 2.95, 10.92, 6.93], [9.31, 7.38, 2.87, 6.99, 6.88, 7.23, 6.63, 7.78, 3.87, 6.26, 7.99, 9.78, 9.99, 8.97, 7.99, 7.46, 6.41, 8.85, 6.41, 8.65, 8.93, 3.99, 2.45, 6.95, 4.8], [12.77, 8.99, 2.77, 7.75, 8.05, 7.92, 8.33, 7.93, 3.75, 6.92, 8.25, 11.4, 10.62, 9.52, 9.06, 6.77, 6.75, 'inf', 7.15, 10.83, 'inf', 4.55, 2.68, 9.82, 4.92], [12.75, 9.78, 2.75, 7.99, 8.7, 8.46, 8.15, 7.93, 3.58, 6.75, 8.82, 11.75, 11.55, 9.95, 8.82, 8.4, 7.11, 'inf', 6.99, 9.31, 11.65, 4.57, 2.63, 8.28, 5.0], [13.0, 9.58, 2.9, 7.95, 8.9, 9.01, 8.5, 9.48, 3.63, 6.58, 9.46, 12.23, 12.25, 9.83, 8.99, 9.06, 7.6, 'inf', 7.3, 9.88, 'inf', 4.23, 2.63, 9.77, 5.28]]


def get_all_times(TAS):
    '''
    Output: List of list of record times for each char ('inf')
    '''
    RTA_TIMES = []
    for char in BTT_CHARS_STAGE_COMMAND:
        RTA_TIMES.append(btt_wr_list(TAS, char))

    # TODO: See output of this after btt_wr_list is implemented
    # TODO: Replace None scores with 'inf'
    # for i in range(len(RTA_TIMES)):
    #     for j in range(len(RTA_TIMES)):     
    #         if float(RTA_TIMES[i][j]) != 0.0:
    #                 description_lines.append(float(score_time))
    #         else:
    #                 description_lines.append(float('inf'))
    # print(RTA_TIMES)
    return RTA_TIMES

def calculate_best_total_THS(result_list):
    '''
    TODO: use a generic function for this. okay for now
    Returns min:sec:ms as a string
    '''
    running_THS_frames = 0

    for result in result_list:
        score = float(result[2]) # string converted to float
        score_frames = int(time_to_frames(score))
        running_THS_frames += score_frames

    total_high_score = frames_to_time_string(running_THS_frames)



    return total_high_score

def calculate_best_total(is_TAS=False, is_full_mm=False):
    '''
    is_full_mm: 
    '''

    RTA_TIMES = get_all_times(is_TAS)
    # RTA_TIMES = RTA_TIMES_MATRIX_TEST
    if is_full_mm:
        # Replace all vanilla times with infinity
        for i in range(len(RTA_TIMES)):
            RTA_TIMES[i][i] = 'inf'
    row_ind, col_ind = linear_sum_assignment(RTA_TIMES) 

    result = []
    for i in range(len(row_ind)):
        # print(BTT_CHARS_STAGE_COMMAND[row_ind[i]] + " on " + BTT_STAGES[col_ind[i]] + " " + "{:.2f}".format(RTA_TIMES[row_ind[i]][col_ind[i]]))
        # Append char, stage, time. Format: <Char> on <Stage> (). At end, Total: THS. All as string
        result.append([BTT_CHARS_STAGE_COMMAND[row_ind[i]], BTT_STAGES[col_ind[i]], "{:.2f}".format(RTA_TIMES[row_ind[i]][col_ind[i]]) ])
    
    THS = calculate_best_total_THS(result)
    result.append(THS)

    return result




if __name__ == "__main__":
    calculate_best_total(is_TAS=False, is_full_mm=True)
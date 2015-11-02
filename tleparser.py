__author__ = 'Ibrahim'


def parse_tle_number(tle_number_string):
    split_string = tle_number_string.split('-')
    if len(split_string) == 3:
        new_number = '-' + str(split_string[1]) + 'e-' + str(int(split_string[2])+1)
    elif len(split_string) == 2:
        new_number = str(split_string[0]) + 'e-' + str(int(split_string[1])+1)
    elif len(split_string) == 1:
        new_number = '0.' + str(split_string[0])
    else:
        raise TypeError('Input is not in the TLE float format')

    try:
        return float(new_number)
    except:
        return None

def parse_tle(name, line1, line2):
    if len(line1) < 69:
        return None
    if len(line2) < 69:
        return None

    result = {}

    result['name'] = str(name)
    result['international_designator'] = line1[9:17].strip()
    result['classification'] = str(line1[7:8])

    try:
        result['mean_motion_dot'] = float(line1[33:43])*2
    except ValueError:
        result['mean_motion_dot'] = None

    try:
        result['mean_motion_ddot'] = parse_tle_number(line1[44:52])*6.0
    except:
        result['mean_motion_ddot'] = None

    result['bstar'] = parse_tle_number(line1[53:61])

    try:
        result['element_number'] = int(line1[64:68].strip())
    except:
        result['element_number'] = None

    try:
        result['satellite_number'] = int(line1[2:7].strip())
    except:
        result['satellite_number'] = None

    try:
        result['inclination'] = float(line2[8:16].strip())
    except:
        result['inclination'] = None

    try:
        result['ra_of_asc_node'] = float(line2[17:25].strip())
    except:
        result['ra_of_asc_node'] = None

    try:
        result['arg_of_perigee'] = float(line2[34:42].strip())
    except:
        result['arg_of_perigee'] = None

    try:
        result['mean_anomaly'] =  float(line2[43:51])
    except:
        result['mean_anomaly'] =  None

    result['eccentricity'] = parse_tle_number(line2[26:33].strip())

    try:
        result['rev_at_epoch'] = int(line2[63:68])
    except:
        result['rev_at_epoch'] = None

    try:
        result['two_digit_year'] = int(line1[18:20])
    except:
        result['two_digit_year'] = None

    if result['two_digit_year']:
        if result['two_digit_year'] > 56:
            result['epoch_year'] = result['two_digit_year']+1900
        else:
            result['epoch_year'] = result['two_digit_year']+2000
    try:
        result['epoch_day'] = float(line1[20:32])
    except:
        result['epoch_day'] = None

    try:
        result['mean_motion'] = float(line2[52:63])
    except:
        result['mean_motion'] = None

    return result
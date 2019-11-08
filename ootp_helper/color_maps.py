def stat_color(stat: int, name: str) -> str:
    if stat > 140:
        s_color = '1A810A'
    elif stat > 120:
        s_color = '40A94A'
    elif stat > 80:
        s_color = 'lightgray'
    elif stat > 60:
        s_color = 'CC4F4F'
    else:
        s_color = '870000'

    return '<font color="{0}">{1:.0f} {2} </font>'.format(s_color, stat, name)


def pitch_color(pitch: int) -> str:
    if pitch > 110:
        s_color = 'FF0000'
    elif pitch > 100:
        s_color = 'EA8A27'
    else:
        s_color = 'lightgray'

    return '<font color="{0}">{1:.0f} PPG </font>'.format(s_color, pitch)


def defense_stat_colors(rat: int) -> str:
    if type(rat) is not int and type(rat) is not float:
        return 'background-color: #FFFFFF'
    if rat > 15:
        return 'background-color: #44bbdd'
    if rat > 5:
        return 'background-color: #117722'
    if rat > -5:
        return 'background-color: #eac117'
    if rat > -15:
        return 'background-color: #dd8033'
    else:
        return 'background-color: #dd0000'

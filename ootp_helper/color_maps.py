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


def rating_colors(rat: int) -> str:
    if type(rat) is not int and type(rat) is not float:
        return '#FFFFFF'
    if rat > 70:
        return '#44bbdd'
    if rat > 55:
        return '#117722'
    if rat > 40:
        return '#eac117'
    if rat > 25:
        return '#dd8033'
    else:
        return '#dd0000'


def background_rating_colors(rat: int) -> str:
    return 'background-color: {}'.format(rating_colors(rat))


def highlight_mwar(mwar: float) -> str:
    if type(mwar) is not int and type(mwar) is not float:
        return 'background-color: #FFFFFF'
    if mwar > 6.5:
        return 'background-color: #44bbdd'
    if mwar > 4.5:
        return 'background-color: #117722'
    if mwar > 3.8:
        return 'background-color: #eac117'
    if mwar > 3:
        return 'background-color: #dd8033'
    else:
        return 'background-color: #dd0000'


def highlight_mwar_change(delta: float) -> str:
    if delta > 0.5:
        return 'background-color: #44bbdd'
    elif delta > 0.3:
        return 'background-color: #32b632'
    elif delta < -0.5:
        return 'background-color: #b63932'
    elif delta < -0.3:
        return 'background-color: #dd8033'
    else:
        return ''


def highlight_og_change(delta: float) -> str:
    if delta > 1:
        return 'background-color: #44bbdd'
    elif delta > 0.5:
        return 'background-color: #32b632'
    elif delta < -1:
        return 'background-color: #b63932'
    elif delta < -0.5:
        return 'background-color: #dd8033'
    else:
        return ''


def highlight_woba(woba: float) -> str:
    if woba < 0.3:
        return 'background-color: transparent'
    else:
        # picking shades of green
        amount_green = max(round(255 - (1500 * (woba - 0.3))), 100)
        amount_other = max(round(255 - (3000 * (woba - 0.3))), 50)

        return 'background-color: rgb({}, {}, {})'.format(amount_other, amount_green, amount_other)


def highlight_fip(fip: float) -> str:
    if fip > 4.5:
        return 'background-color: transparent'
    else:
        # picking shades of green
        amount_green = max(round(255 + (100 * (fip - 4.5))), 100)
        amount_other = max(round(255 + (200 * (fip - 4.5))), 50)

        return 'background-color: rgb({}, {}, {})'.format(amount_other, amount_green, amount_other)

def fermControl(serialCon, setpoint, temp, auto):

    if auto is True:
        if setpoint < temp:
            serialCon.write('PT')
        else:
            serialCon.write('PF')

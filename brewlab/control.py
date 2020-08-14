def fermControl(serialCon, setpoint, temp, auto):

    if auto is True:
        if setpoint < temp:
            serialCon.write('PT'.encode())
        else:
            serialCon.write('PF'.encode())

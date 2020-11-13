def fermControl(serialCon, setpoint, temp, auto):
    """
    Simulates bang control scheme for fermenter
    """

    if auto is True:
        if setpoint < temp:
            serialCon.write('PT'.encode())
        else:
            serialCon.write('PF'.encode())

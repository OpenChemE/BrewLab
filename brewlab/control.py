def get_on_command(ferm):

    if ferm == "F1":
        return "PT1"
    elif ferm == "F2":
        return "PT2"
    elif ferm == "F3":
        return "PT3"

    return None


def get_off_command(ferm):

    if ferm == "F1":
        return "PF1"
    elif ferm == "F2":
        return "PF2"
    elif ferm == "F3":
        return "PF3"

    return None


def fermControl(serialCon, ferm, measured):
    """
    Simulates bang control scheme for fermenter
    """

    if ferm.auto:
        # If measured temp is greater than setpoint (ferm.temp)
        # Turn on Pump
        if ferm.temp < measured:
            command = get_on_command(ferm.id)
            serialCon.write(command.encode())
        else:
            command = get_off_command(ferm.id)
            serialCon.write(command.encode())

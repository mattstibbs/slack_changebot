def represents_an_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

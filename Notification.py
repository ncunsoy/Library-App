class Notification:
    _userID=-1
    _message=None
    _date=None

    def __init__(self,userID,message,date):
        self._userID=userID
        self._message=message
        self._date=date

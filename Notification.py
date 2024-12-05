class Notification:
    _userID=-1
    _message=None
    _date=None

    def __init__(self,userID,message,date):
        self._userID=userID
        self._message=message
        self._date=date

    def delete_notification(self, controller):
        try:
            query = "DELETE FROM Notification WHERE UserID = ? AND Message = ? AND NotificationDate = ?"
            controller._cursor.execute(query, (self._userID, self._message, self._date))
            controller._conn.commit()
            print("Bildirim başarıyla silindi.")
        except Exception as e:
            print(f"Bildirim silinirken hata oluştu: {e}")
            controller._conn.rollback()
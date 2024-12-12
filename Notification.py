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

import unittest
from unittest.mock import MagicMock
from Notification import Notification

class TestNotification(unittest.TestCase):

    def setUp(self):
        # Mock DatabaseController
        self.controller = MagicMock()
        
        # Test için Notification nesnesi oluşturuluyor
        self.notification = Notification(
            userID=1,
            message="Test Notification",
            date="2024-12-12"
        )
        
        # Mock veri
        self.controller._cursor.execute.return_value = None  # Mock execute
        self.controller._conn.commit.return_value = None  # Mock commit
        self.controller._conn.rollback.return_value = None  # Mock rollback
    
    def test_delete_notification_success(self):
        # delete_notification metodunu test et
        self.controller._cursor.execute.side_effect = None  # No error
        self.controller._conn.commit.side_effect = None  # No error
        
        self.notification.delete_notification(self.controller)
        
        # commit'in çağrıldığını doğrula
        self.controller._conn.commit.assert_called_once()
        print("Test passed for successful deletion.")
    
    def test_delete_notification_failure(self):
        # delete_notification metodunda hata simülasyonu
        self.controller._cursor.execute.side_effect = Exception("Database error")
        self.controller._conn.rollback.side_effect = None  # rollback'yi simüle et
        
        self.notification.delete_notification(self.controller)
        
        # rollback'ın çağrıldığını doğrula
        self.controller._conn.rollback.assert_called_once()
        print("Test passed for failed deletion.")
    
if __name__ == '__main__':
    unittest.main()            

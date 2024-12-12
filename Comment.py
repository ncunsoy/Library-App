class Comment:
    _commentID=-1
    _userID=-1
    _bookISBN=-1
    _commentText=None
    _commentDate=None

    def __init__(self,commentID,userID,bookISBN,commentText,commentDate):
        self._commentID=commentID
        self._userID=userID
        self._bookISBN=bookISBN
        self._commentText=commentText
        self._commentDate=commentDate


    def getCommentID(self):
        return self._commentID
    
    def getUserID(self):
        return self._userID
    
    def getBookISBN(self):
        return self._bookISBN
    
    def getCommentText(self):
        return self._commentText
    
    def getCommentDate(self):
        return self._commentDate
    
    def update_comment_text(self, new_text, controller):
        """Yorum metnini güncelle ve veritabanına kaydet."""
        try:
            query = "UPDATE Comment SET CommentText = ? WHERE CommentID = ?"
            controller._cursor.execute(query, (new_text, self._commentID))
            controller._conn.commit()
            self._commentText = new_text
            print("Yorum başarıyla güncellendi.")
        except Exception as e:
            print(f"Yorum güncellenirken hata oluştu: {e}")
            controller._conn.rollback()

    def delete_comment(self, controller):
        """Yorumu veritabanından sil."""
        try:
            query = "DELETE FROM Comment WHERE CommentID = ?"
            controller._cursor.execute(query, (self._commentID,))
            controller._conn.commit()
            print("Yorum başarıyla silindi.")
        except Exception as e:
            print(f"Yorum silinirken hata oluştu: {e}")
            controller._conn.rollback()


import unittest
from unittest.mock import MagicMock

class TestComment(unittest.TestCase):

    def setUp(self):
        # Mock controller nesnesi ve veritabanı bağlantısı
        self.controller = MagicMock()
        self.controller._conn = MagicMock()  # Veritabanı bağlantısı için mock nesnesi
        self.controller._cursor = MagicMock()  # Cursor için mock nesnesi

        # Comment nesnesi oluşturuluyor
        self.comment = Comment(1, 2, "978-3-16-148410-0", "Test Comment", "2024-12-12")

    def test_update_comment_text(self):
        # Yorum metnini güncelleme test et
        new_text = "Updated Comment Text"
        self.controller._cursor.execute.side_effect = None  # Hata olmayacak şekilde ayarlandı
        self.controller._conn.commit.side_effect = None  # Commit simüle edildi

        # Metni güncelle
        self.comment.update_comment_text(new_text, self.controller)

        # Yeni metnin doğru şekilde ayarlandığını kontrol et
        self.assertEqual(self.comment.getCommentText(), new_text)
        self.controller._cursor.execute.assert_called_with(
            "UPDATE Comment SET CommentText = ? WHERE CommentID = ?",
            (new_text, self.comment.getCommentID())
        )
        self.controller._conn.commit.assert_called()

    def test_update_comment_text_error_handling(self):
        # Yorum metnini güncellerken hata durumu
        new_text = "Updated Comment Text"
        self.controller._cursor.execute.side_effect = Exception("Database error")
        self.controller._conn.rollback.side_effect = None  # rollback simüle edildi

        # Metni güncelleme
        self.comment.update_comment_text(new_text, self.controller)

        # rollback'ın çağrıldığını kontrol et
        self.controller._conn.rollback.assert_called()

    def test_delete_comment(self):
        # Yorum silme test et
        self.controller._cursor.execute.side_effect = None  # Hata olmayacak şekilde ayarlandı
        self.controller._conn.commit.side_effect = None  # Commit simüle edildi

        # Yorum silme
        self.comment.delete_comment(self.controller)

        # Yorumun silindiği doğrulandı
        self.controller._cursor.execute.assert_called_with(
            "DELETE FROM Comment WHERE CommentID = ?", 
            (self.comment.getCommentID(),)
        )
        self.controller._conn.commit.assert_called()

    def test_delete_comment_error_handling(self):
        # Yorum silme sırasında hata durumu
        self.controller._cursor.execute.side_effect = Exception("Database error")
        self.controller._conn.rollback.side_effect = None  # rollback simüle edildi

        # Yorum silme
        self.comment.delete_comment(self.controller)

        # rollback'ın çağrıldığını kontrol et
        self.controller._conn.rollback.assert_called()


if __name__ == '__main__':
    unittest.main()

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
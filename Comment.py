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
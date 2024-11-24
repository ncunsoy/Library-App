from sqlalchemy import create_engine
import pandas as pd

user=pd.read_csv("D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/users.csv")
staff=pd.read_csv("D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/staffs.csv")
book=pd.read_csv("D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/books.csv")
reservation=pd.read_csv("D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/reservation.csv")
comment=pd.read_csv("D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/comment.csv")
readingList=pd.read_csv("D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/readingList.csv")
notification=pd.read_csv("D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/notification.csv")


engine =create_engine('sqlite:///LibraryApp.db')

user.to_sql('User',con=engine,if_exists='replace')
staff.to_sql('Staff',con=engine,if_exists='replace')
book.to_sql('Book',con=engine,if_exists='replace')
reservation.to_sql('Reservation',con=engine,if_exists='replace')
comment.to_sql('Comment',con=engine,if_exists='replace')
readingList.to_sql('ReadingList',con=engine,if_exists='replace')
notification.to_sql('Notification',con=engine,if_exists='replace')
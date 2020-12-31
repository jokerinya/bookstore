from flask import Flask, jsonify ,request, abort, make_response
from flaskext.mysql import MySQL
# import json

app = Flask(__name__)

# db_endpoint = open("/home/ec2-user/dbserver.endpoint", 'r', encoding='UTF-8') 
# db_password = open("/home/ec2-user/dbserver.passwd", 'r', encoding='UTF-8') 

# Configure mysql database
# app.config['MYSQL_DATABASE_HOST'] = db_endpoint.readline().strip()
app.config['MYSQL_DATABASE_HOST'] = 'database'
# For local development purposes host.docker.internal can be used
# app.config['MYSQL_DATABASE_HOST'] = 'host.docker.internal'
app.config['MYSQL_DATABASE_USER'] = 'jokerinya'
# app.config['MYSQL_DATABASE_PASSWORD'] = db_password.readline().strip()
app.config['MYSQL_DATABASE_PASSWORD'] = "Ankara06"
app.config['MYSQL_DATABASE_DB'] = 'clarusway'
app.config['MYSQL_DATABASE_PORT'] = 3306
# db_endpoint.close()
# db_password.close()
mysql = MySQL()
mysql.init_app(app)
connection = mysql.connect()
connection.autocommit(True)
cursor = connection.cursor()

# execute the code only ONCE
def db_start():
    drop_table="""
    DROP TABLE IF EXISTS bookstore;
    """
    bookstore_table="""
    CREATE TABLE bookstore (
    book_id INT NOT NULL AUTO_INCREMENT,
    title varchar(50) NOT NULL,
    author varchar(50),
    is_sold boolean,
    PRIMARY KEY (book_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    sample_data="""
    INSERT INTO bookstore(title, author, is_sold)
    VALUES
        ("Live in Vegas","Buddy Rich", 1 ),
        ("Malibu Nights" ,"Candido", 0),
        ("Dee DEEEEEE","Charlie Byrd", 0);
    """

    cursor.execute(drop_table)
    cursor.execute(bookstore_table)
    cursor.execute(sample_data)

# Universal query making
def do_the_query(query):
    cursor.execute(query)
    row = cursor.fetchone()  # tuple type
    if row == None:
        result = {
            "book_id" : "Not Found", 
            "title": "Not Found", 
            "author": "Not Found", 
            "is_sold": "Not Found"
        }
    else:
        result = {
            "book_id" : row[0], 
            "title": row[1], 
            "author": row[2], 
            "is_sold": row[3]
        }
    return result

# Query for find one book with id
def find_book_from_id(id):
    query=f"SELECT * FROM bookstore WHERE book_id like '%{id}%';"
    return do_the_query(query)

# Query for find one book with title
def find_book_from_name(title):
    query=f"SELECT * FROM bookstore WHERE title='{title}';"
    return do_the_query(query)


# Query add one book
def add_one_book(book):
    query=f"""INSERT INTO bookstore(title, author, is_sold) VALUES ("{book["title"]}", "{book["author"]}", "{book["is_sold"]}");"""
    cursor.execute(query)

# Query update one book
def update_one_book(book):
    query=f"""UPDATE bookstore SET title="{book["title"]}", author="{book["author"]}", is_sold="{book["is_sold"]}" WHERE book_id="{book["book_id"]}";"""
    cursor.execute(query)

# Query delete book
def delete(book_id):
    query=f"DELETE FROM bookstore WHERE book_id = {book_id}"
    cursor.execute(query)

# Index Page
@app.route("/")
def index():
    return "Welcome Dear Customer"

# Get all books
@app.route("/books")
def get_books():
    query=f"SELECT * FROM bookstore;"
    cursor.execute(query)
    raw_result = cursor.fetchall()  # tuple type
    result = [{"book_id": row[0], "title" : row[0], "author": row[1], "is_sold": row[2]} for row in raw_result]
    if not any(result):
        result = [{"title" : "Not Found", "author": "Not Found"}]
    return jsonify({"books:": result})

# Get one book from id
@app.route("/books/<book_id>")
def get_one_book(book_id):
    return jsonify({"book":find_book_from_id(book_id)})

@app.route("/books/<book_id>", methods=["PUT"])
def update_book(book_id):
    # db check
    res = find_book_from_id(book_id)
    # No record
    if res["title"] == "Not Found":
        return f"""No record with id num: {book_id}, Make your 'POST' request to '/books' path with new info"""
    # db ok
    book = request.json
    book["book_id"] = book_id
    update_one_book(book)
    return jsonify({"old record": res}, {"new record": book})

# Add one book
@app.route("/books", methods=["POST"])
def add_book():
    # check for if request is ok
    if not request.json or not 'title' in request.json:
        abort(400)
    book = request.json
    # check db for if any records or sold-out
    db_result = find_book_from_name(book["title"])
    # not found in db, new record
    if db_result["title"] == "Not Found":
        add_one_book(book)
        return jsonify({"Newly added book": book})
    # update the record is_sold part
    return f"""There is record with title=> {db_result}, \n 
            Please make 'PUT' request to '/books/{db_result["book_id"]}' with new info"""

# Delete one book
@app.route("/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    # check db
    db_res = find_book_from_id(book_id)
    if db_res["title"] == "Not Found":
        return f"""No record with id num: {book_id}"""
    # There is record on the db
    delete(book_id)
    return jsonify({"Deleted record": db_res})

if __name__ == "__main__":
    db_start()
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=80)
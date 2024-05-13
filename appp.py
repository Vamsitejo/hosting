from flask import Flask, request, render_template
from datetime import datetime
import pytz
from tabulate import tabulate
import mysql.connector

app = Flask(__name__)

# MySQL database connection configuration
mysql_config = {
    'host': '65.2.113.241',
    'port': 3306,
    'user': 'dev-frappe',
    'password': 'N2TgH0gq4OXc',
    'database': 'frappe' 
}

def get_mysql_connection():
    return mysql.connector.connect(**mysql_config)

def create_table_if_not_exists():
    # Connect to MySQL database
    connection = get_mysql_connection()
    cursor = connection.cursor()

    # SQL query to create table if not exists
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ornithon (
        id INT AUTO_INCREMENT PRIMARY KEY,
        created_at DATETIME,
        cracked INT,
        jumbo INT,
        selected INT,
        table_count INT,
        wasted INT
    )
    """

    # Execute the query
    cursor.execute(create_table_query)

    # Commit changes and close connection
    connection.commit()
    connection.close()

def insert_data(payload):
    # Connect to MySQL database
    connection = get_mysql_connection() 
    cursor = connection.cursor()

    # Prepare SQL query to insert data
    query = "INSERT INTO ornithon (created_at, cracked, jumbo, selected, table_count, wasted) VALUES (%s, %s, %s, %s, %s, %s)"

    # Convert created_at to UTC time
    created_at = datetime.now(pytz.utc).isoformat()

    # Extract required fields from payload
    field1 = payload['Cracked']
    field2 = payload['Jumbo']
    field3 = payload['Selected']
    field4 = payload['Table']
    field5 = payload['Wasted']

    # Execute the SQL query
    cursor.execute(query, (created_at, field1, field2, field3, field4, field5))

    # Commit changes and close connection
    connection.commit()
    connection.close()

def get_data_from_mysql():
    # Connect to MySQL database
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)

    # Prepare SQL query to select data
    query = "SELECT * FROM ornithon"

    # Execute the SQL query
    cursor.execute(query)

    # Fetch all rows
    data = cursor.fetchall()

    # Close connection
    connection.close()

    return data

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    print(data)
    insert_data(data['payload'])
    return "Data inserted into MySQL successfully"

@app.route('/view-data')
def display_data():
    # Get data from MySQL database
    data = get_data_from_mysql()

    # Format data for tabulate
    formatted_data = []
    for row in data:
        # Convert UTC time to Indian Standard Time (IST)
        created_at_utc = row['created_at']
        ist = pytz.timezone('Asia/Kolkata')
        created_at_ist = created_at_utc.astimezone(ist)
        
        # Format IST datetime as string
        row['created_at'] = created_at_ist.strftime("%Y-%m-%d %H:%M:%S")
        formatted_data.append(row)

    # Generate HTML table
    table = tabulate(formatted_data, headers="keys", tablefmt="html")

    return render_template('index.html', table=table)


if __name__ == "__main__":
    # Create table if not exists
    create_table_if_not_exists()
    
    # Run the application
    app.run(debug=True)

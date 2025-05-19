Jupyter Notebokk commands.
##############################################################################################################################
##############################################################################################################################
1
##############################################################################################################################
##############################################################################################################################
#Importing libraries.
import pyodbc
import random
import string

#Function to generate new customer ids.
def generate_customer_id():
    first_part = random.choice(string.ascii_uppercase)
    second_part = f"{random.randint(0, 999):03}"
    third_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
    return f"{first_part}{second_part}-{third_part}"


#Establish connection to the SQL Server Database.
conn = pyodbc.connect(r"Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=CarServiceDBVideo;Trusted_Connection=yes;")
cursor = conn.cursor()

#Data for the new service booking.
#Customer information.
cust_forenames = "James"
cust_surname = "Law"
cust_email = "j.law@ulster.ac.uk"
cust_phoneno = "41727568003"

#Car information.
registration = "AF500WWJ"
car_make = "Volkswagen"
car_model = "Golf"
date_of_manufacture = "2014-05-25"
dropoff_date = "2020-06-25"
dropoff_time = "14:30:00"
work_required = "MOT check-up"
milage = 45000

#Check if customer exists.
customer_query = """
    SELECT customer_id  --Find the customer id.
    FROM Customer --From the customer table.
    WHERE cust_forenames = ? --Where the specified forenames and surnames are.
    AND cust_surname = ?;
"""

#Execute the query.
cursor.execute(customer_query, (cust_forenames, cust_surname))
customer_row = cursor.fetchone()

#If there is no cusmter_id associated with the customer forenames and surname.
if customer_row is None:
    #while loop to make sure the new customer_+id is unique.
    while True:
        customer_id = generate_customer_id()
        #Check if the generated customer ID is unique.
        cursor.execute("SELECT 1 "
                       "FROM Customer "
                       "WHERE customer_id = ?", (customer_id,))
        if not cursor.fetchone():
            break  #Exit the loop if the ID is unique.

    #SQL Query to use the stored procedure to check and add the customer in the database.
    cursor.execute("""
        EXEC InsertCustomerIfNotExists 
            @customer_id = ?,
            @cust_forenames = ?,
            @cust_surname = ?,
            @cust_email = ?,
            @cust_phoneno = ?;
    """, (customer_id, cust_forenames, cust_surname, cust_email, cust_phoneno))
    conn.commit()

#SQL Query to use the stored procedure to check the car is in the database and add it into the table if it is not
cursor.execute("""
    EXEC InsertCarIfNotExists 
        @registration = ?, 
        @make = ?, 
        @model = ?, 
        @date_of_manufacture = ?;
""", (registration, car_make, car_model, date_of_manufacture))
conn.commit()

#Get the latest service ID.
service_id_query = """
    SELECT TOP 1 service_id --Finds the latest service_ids.
    FROM Service --From the service table.
    ORDER BY service_id DESC; --Orders the service_ids in desending order.
"""

#Execute the query.
cursor.execute(service_id_query)
last_service_row = cursor.fetchone()

#Logic to make a new service ID.
if last_service_row:
    last_service_id = last_service_row[0]
    #Increment the numeric part of the service ID.
    prefix, number = last_service_id.split('-')
    new_service_id = f"{prefix}-{int(number) + 1}"
else:
    #If there are no previous services in the database, start from 001.
    new_service_id = "S2006-001"

#SQL Query to insert the new service into the database.
insert_service_query = """
    INSERT INTO Service (service_id, dropoff_date, dropoff_time, work_required, milage, next_service, registration, customer_id)
    VALUES (?, ?, ?, ?, ?, NULL, ?, ?);
"""
#The trigger 'trg_AfterServiceInsert' will now execute adding the information into ServiceEmployee.

#Execute the query.
cursor.execute(insert_service_query,(new_service_id, dropoff_date, dropoff_time, work_required, milage, registration, customer_id))
conn.commit()

#Output confirmation.
print(f"Service booking added successfully with Service ID: {new_service_id}")

##############################################################################################################################
##############################################################################################################################
2
##############################################################################################################################
##############################################################################################################################
#Business Process 2
#Importing libraries.
import pandas as pd
import pyodbc

#Establish connection to the SQL Server Database.
conn = pyodbc.connect(r"Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=CarServiceDBVideo;Trusted_Connection=yes;")
cursor = conn.cursor()

#Input the new service registration and dropoff date.
new_service_registration = 'SEZ 5629'
new_service_dropoff_date = '2020-06-17'

#SQL Query to find the mechanics who have worked on previous services of the car
#and count how many jobs they are involved in on the dropoff date of the new service.
query = """
    WITH PreviousMechanics AS ( --Defines a Common Table Expression (CTE) named PreviousMechanics.
        SELECT DISTINCT se.employee_id, e.emp_forenames, e.emp_surname --Select the employee IDs, forenames and surnames.
        FROM ServiceEmployee se --From the ServiceEmployee table.
        JOIN Service s ON se.service_id = s.service_id --Joins Service table to match service IDs.
        JOIN Employee e ON se.employee_id = e.employee_id --Joins Employee table to match employee IDs.
        WHERE s.registration = ? --Filters for a specific vehicle registration.
    )
    SELECT pm.employee_id, pm.emp_forenames, pm.emp_surname,  --Selects the employee IDs, forenames and surnames from the PreviousMechanics CTE.
           COUNT(se.service_id) AS jobs_today --Counts the number of jobs assigned today.
    FROM PreviousMechanics pm --From the CTE containing previous mechanics.
    LEFT JOIN ServiceEmployee se ON pm.employee_id = se.employee_id --Joins ServiceEmployee table to match mechanics.
    LEFT JOIN Service s ON se.service_id = s.service_id --Joins Service table to match services.
    WHERE s.dropoff_date = ? --Filters for jobs with today's drop-off date.
    GROUP BY pm.employee_id, pm.emp_forenames, pm.emp_surname --Groups results by employee details.
    HAVING COUNT(se.service_id) > 0 --Ensures only employees with jobs today are included.
    ORDER BY jobs_today DESC; --Orders the mechanics by the number of jobs, from most to least.
"""

#Execute the query.
cursor.execute(query, (new_service_registration, new_service_dropoff_date))
rows = cursor.fetchall()

#Create a DataFrame from the query result.
data = []
for row in rows:
    employee_name = f"{row[1]} {row[2]}"  #Combine forename and surname name into a whole name.
    jobs_today = row[3]
    data.append([employee_name, jobs_today])

#Create DataFrame for better display.
result_table = pd.DataFrame(data, columns=['Employee Name', 'Jobs on Service Day'])

#Output the results.
result_table

##############################################################################################################################
##############################################################################################################################
3
##############################################################################################################################
##############################################################################################################################
#Business Process 3
#Importing libraries.
import pandas as pd
import pyodbc

#Establish connection to the SQL Server Database.
conn = pyodbc.connect(r"Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=CarServiceDBVideo;Trusted_Connection=yes;")
cursor = conn.cursor()

#Input dates for filtering the services
start_date = '2020-06-17'
end_date = '2020-06-18'

#SQL Query to get the total time spent per mechanic within the date range.
query = """
    SELECT e.employee_id, e.emp_forenames, e.emp_surname, --Selects the employee ID, forename and surname
           SUM(DATEDIFF(SECOND, '00:00:00', se.time_spent)) AS total_seconds --Calculates the total time spent by each employee in seconds., DATEDIFF returns the difference between two dates, as an integer
    FROM ServiceEmployee se --From the ServiceEmployee table, links services to employees.
    JOIN Employee e ON se.employee_id = e.employee_id --Joins the Employee table to match employee IDs.
    JOIN Service s ON se.service_id = s.service_id --Joins the Service table to match service IDs.
    WHERE s.dropoff_date BETWEEN ? AND ? --Filters services based on a date range for drop-off dates.
    GROUP BY e.employee_id, e.emp_forenames, e.emp_surname --Groups results by each employee's details.
    ORDER BY total_seconds DESC; --Orders employees by the total time spent, from most to least.
"""

#Execute the query.
cursor.execute(query, (start_date, end_date))
rows = cursor.fetchall()

#Create a DataFrame from the query result.
data = []
for row in rows:
    #Convert total seconds to minutes.
    total_minutes = row[3] / 60
    employee_name = f"{row[1]} {row[2]}"
    data.append([employee_name, total_minutes])

#Create DataFrame for better output.
result_table = pd.DataFrame(data, columns=['Employee Name', 'Total Time (minutes)'])

#Output the results.
result_table

##############################################################################################################################
##############################################################################################################################
4
##############################################################################################################################
##############################################################################################################################
#Business Process 4
#Importing libraries.
import pyodbc
import pandas as pd

#Establish connection to the SQL Server Database.
conn = pyodbc.connect(r"Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=CarServiceDBVideo;Trusted_Connection=yes;")
cursor = conn.cursor()

#Start and end date for the query.
start_date = '2021-06-21'
end_date = '2021-06-24'

#SQL Query to get the list of customers and the relevant information
query = """
    SELECT Customer.cust_forenames, Customer.cust_surname, Customer.cust_email, --Selects the forename, surname and email of the customer
    Car.make, Car.registration, --Selects the make and registration of the car
    Service.next_service --Selects the date of the next scheduled service.
    FROM Customer --From the Customer table, containing customer details.
    JOIN Service ON Customer.customer_id = Service.customer_id --Joins the Service table to match customers with their services.
    JOIN Car ON Service.registration = Car.registration --Joins the Car table to match cars with their service records.
    WHERE Service.next_service BETWEEN ? AND ?; --Filters for services scheduled within a specified date range.
"""

#Execute the query.
cursor.execute(query, (start_date, end_date))
rows = cursor.fetchall()

#Create a DataFrame from the query result.
data = []
for row in rows:
    customer_name = f"{row[0]} {row[1]}"  #Combine forename and surname name into a whole name.
    data.append([customer_name, row[2], row[3], row[4], row[5]])

#Create DataFrame for better display.
result_table = pd.DataFrame(data, columns=['Customer Name', 'Customer email', 'Car make', 'Registration', 'Date of next service'])

#Output the results.
result_table

##############################################################################################################################
##############################################################################################################################
5
##############################################################################################################################
##############################################################################################################################
#Business Process 5
#Importing libraries.
import pandas as pd
import pyodbc

#Establish connection to the SQL Server Database.
conn = pyodbc.connect(r"Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=CarServiceDBVideo;Trusted_Connection=yes;")
cursor = conn.cursor()

#Input employee's employee_id, unavailable period start, and end dates.
employee_id = 'E9274'
unavailable_from = '2020-06-22'
unavailable_to = '2020-06-24'

#SQL Query to insert the employee's unavailability period into the EmployeeAviability table.
insert_query = """
    INSERT INTO EmployeeAviability (employee_id, unavailable_from, unavailable_to)
    VALUES (?, ?, ?);
"""
cursor.execute(insert_query, (employee_id, unavailable_from, unavailable_to))
conn.commit()

#Query to find services the mechanic may be involved in during their unavailability period.
query = """
    SELECT se.service_id, se.employee_id, e.emp_forenames, e.emp_surname, s.dropoff_date, s.dropoff_time, s.work_required --Selects the service id; the employees id, forename and surname; the drop-off date and time of the service and work required
    FROM ServiceEmployee se --From the ServiceEmployee table, linking employees to services.
    JOIN Service s ON se.service_id = s.service_id --Joins the Service table to match services with their details.
    JOIN Employee e ON se.employee_id = e.employee_id --Joins the Employee table to match employees with their details.
    WHERE se.employee_id = ? --Filters for services assigned to a specific employee.
    AND s.dropoff_date BETWEEN ? AND ? --Filters for services within a specified date range.
    ORDER BY s.dropoff_date, s.dropoff_time; --Orders the results by drop-off date and time.
"""

#Execute the query.
cursor.execute(query, (employee_id, unavailable_from, unavailable_to))
rows = cursor.fetchall()

#Create a DataFrame from the query result.
data = []
for row in rows:
    employee_name = f"{row[2]} {row[3]}"
    data.append([row[0], employee_name, row[4], row[5], row[6]])

#Create DataFrame for better display.
result_table = pd.DataFrame(data, columns=['Service ID', 'Employee Name', 'Service Date', 'Service Time', 'Work Required'])

#Output the results.
result_table


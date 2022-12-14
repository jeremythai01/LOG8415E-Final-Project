import pymysql.cursors

class DBConnector:

    def __init__(self, manager_ip):
        self.connection = self.create_connection(manager_ip, 3306, 'user', 'password', 'sakila')
        pass


    def create_connection(self, host, port, user, password, database):

        # Connect to the database
        connection = pymysql.connect(host=host,
                                    port=port,
                                    user=user,
                                    password=password,
                                    database=database,
                                    autocommit=True)

        return connection


    def execute_query(self, query):

        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                #sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
        
                cursor.execute(query)
                print(cursor.fetchall())
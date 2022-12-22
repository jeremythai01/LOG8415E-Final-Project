import pymysql
import constant


class DBConnector:
    """Database connector used to connect application to mysql database."""
    def __init__(self, manager_pdns):
        """Constructor
        
        Parameters
        ----------
        manager_pdns :  string
                        Private DNS of cluster manager
        """
        self.connection = self.create_connection(manager_pdns)
        pass


    def create_connection(self, host):
        """Create connection to the MySQL database.
        
        Parameters
        ----------
        host :  string
                The host where the database server is located
       
        Returns
        -------
        connection : created database connection
        """
        # Connect to the database
        connection = pymysql.connect(host=host,
                                    port=constant.MYSQL_PORT,
                                    user=constant.MYSQL_USERNAME,
                                    password=constant.MYSQL_PASSWORD,
                                    database='sakila',
                                    autocommit=True)

        return connection


    def execute_query(self, query):
        """Execute SQL query using database connection cursor.
        
        Parameters
        ----------
        query : string
                query to be executed
        """
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                print(cursor.fetchall())
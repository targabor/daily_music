class SnowflakeCredentials:
    """Helps to store and work with credentials in the different uses"""

    def __init__(self, line=''):
        """Constructor for SnowflakeCredentials class

        Args:
            line (str, optional): If it's created from cred.ini, it'll contain the needed data. Defaults to ''.
        """
        if line == '':
            self.user = ''
            self.password = ''
            self.account = ''
            self.warehouse = ''
            self.database = ''
            self.schema = ''
        else:
            splitted = line.split(';')
            self.user = splitted[1]
            self.password = splitted[2]
            self.account = splitted[3]
            self.warehouse = splitted[4]
            self.database = splitted[5]
            self.schema = splitted[0]

    def get_credentialsFor(schemaName: str):
        """Returns the login credentials stored in "cred.ini"

        Args:
            schemaName (str): Name of the schema you want to access

        Returns:
            SnowflakeCredentials: It contains all the necessary data to access the given schema in Snowflake.
        """
        return_credential = None
        with open('', 'r') as cred_in:
            for line in cred_in.readlines():
                if line.startswith(schemaName):
                    return_credential = SnowflakeCredentials(line)
                    break

        if return_credential is not None:
            return return_credential
        else:
            raise Exception(
                f'The {schemaName} schema does not exists in the cred file!')

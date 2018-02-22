class User(object):
    """
    User object to handle prompts if no user name
    or password were provided when running the Client()
    """

    def __init__(self, user=None, pwd=None):
        self.user_name = user
        self.user_pwd = pwd

    def set_user(self):
        """
        Get user name from user
        :return: String, user name
        """
        if not self.user_name:
            while not self.user_name:
                self.user_name = input("funpdbe user name: ")
        return self.user_name

    def set_pwd(self):
        """
        Get user password from user
        :return: String, user password
        """
        if not self.user_pwd:
            while not self.user_pwd:
                self.user_pwd = input("funpdbe password: ")
        return self.user_pwd

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
        Set user name
        """
        self.user_name = self.set_attribute(self.user_name, "funpdbe user name: ")

    def set_pwd(self):
        """
        Set password
        """
        self.user_pwd = self.set_attribute(self.user_pwd, "funpdbe password: ")

    def set_attribute(self, attribute, text):
        """
        Set attribute to user input
        :param attribute:
        :param text:
        :return:
        """
        value = attribute
        if not value:
            while not value:
                value = input(text)
        return value


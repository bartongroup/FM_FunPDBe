from funpdbe_client.constants import CLIENT_ERRORS
from funpdbe_client.logger_config import generic_error


def check_exists(value, error, component_logger):
    """
    Check if a value is not none, and
    log error message if it is
    :param value: Any
    :param error: String
    :param component_logger: Logger instance
    :return: Boolean
    """
    if value:
        return True
    component_logger.log().error(CLIENT_ERRORS[error])
    return False


def check_status(response, expected, component_logger):
    """
    Check if status code is what is expected
    and log message accordingly
    :param response: Response
    :param expected: Int
    :param component_logger: Logger instance
    :return: None
    """
    if response.status_code == expected:
        component_logger.log().info("[%i] SUCCESS" % response.status_code)
    else:
        generic_error()
        component_logger.log().error("[%i] FAIL - %s" % (response.status_code, response.text))

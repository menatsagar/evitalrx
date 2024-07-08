from uuid import UUID


def is_valid_uuid(uuid_to_test):
    """
    Check if a given string is a valid UUID.

    Parameters:
    uuid_to_test (str): A string to be tested if it is a valid UUID.

    Returns:
    bool: True if the input string is a valid UUID, False otherwise.
    """
    try:
        uuid_obj = UUID(uuid_to_test)
    except ValueError:
        return False
    except Exception as e:
        return False
    return str(uuid_obj) == uuid_to_test

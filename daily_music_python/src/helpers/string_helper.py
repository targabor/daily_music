def compare_string(str1: str, str2: str) -> bool:
    """Compares two strings returns True, if there is less than 6 differences between them, if there is more,
    it returns False.

    Args:
        str1 (str): first string to compare
        str2 (str): second string to compare

    Returns:
        bool: True if there is less than 6 differences, False if there is more.
    """
    diff_count = 0

    for i in range(min(len(str1), len(str2))):
        if str1[i] != str2[i]:
            diff_count += 1
            if diff_count > 6:
                return False

    diff_count += abs(len(str1) - len(str2))
    return diff_count < 6

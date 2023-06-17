def remove_non_alphanumeric_chars(input_string: str):
    """
    Removes non-alphanumeric characters from the input string.

    Args:
        input_string (str): The string to remove non-alphanumeric characters from.

    Returns:
        str: The input string with non-alphanumeric characters removed.

    Example:
        >>> cleaned_string = remove_non_alphanumeric_chars("Rock N' Roll!")
        >>> print(cleaned_string)
        'RockNRoll'
    """
    return "".join([char for char in input_string if char.isalnum()])

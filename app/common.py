def binary_search(arr, num):
    """
    This function searches for a specific number in a sorted array using binary search.

    Parameters:
    arr (list): The sorted array to search.
    num (int or float): The number to find in the array.

    Returns:
    int: The index of the number if found, otherwise -1.
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2

        # Check if num is present at mid
        if arr[mid] == num:
            return mid
        # If num is greater, ignore left half
        elif arr[mid] < num:
            left = mid + 1
        # If num is smaller, ignore right half
        else:
            right = mid - 1

    # If we reach here, the element was not present
    return -1

def find_number_in_array(arr, num):
    """
    This function searches for a specific number in an array.
    It sorts the array first and then uses binary search.

    Parameters:
    arr (list): The array to search.
    num (int or float): The number to find in the array.

    Returns:
    int: The index of the number if found, otherwise -1.
    """
    # Sort the array
    sorted_arr = sorted(arr)

    # Perform binary search
    index_in_sorted = binary_search(sorted_arr, num)

    if index_in_sorted == -1:
        return None
    else:
        # Find the index of the number in the original array
        return arr.index(sorted_arr[index_in_sorted])

def compare_name_lists(file_path):
    try:
        with open(file_path, 'r') as file:
            # Read the content of the file
            content = file.read()

        # Split the content into two lists based on the separator
        parts = content.split('#####')
        if len(parts) != 2:
            print("Error: The file must contain two lists separated by '#####'.")
            return

        # Process the lists
        list1 = [name.strip() for name in parts[0].strip().splitlines()]
        list2 = [name.strip() for name in parts[1].strip().splitlines()]

        # Find missing names
        missing_from_list1 = sorted(set(list2) - set(list1))
        missing_from_list2 = sorted(set(list1) - set(list2))

        # Display the results
        print("Names missing from List 1 (present in List 2):")
        for name in missing_from_list1:
            print(name)

        print("\nNames missing from List 2 (present in List 1):")
        for name in missing_from_list2:
            print(name)

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Replace 'names.txt' with the path to your text file
file_path = 'names.txt'
compare_name_lists(file_path)

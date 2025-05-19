# Define a function to find unique names
def find_unique_names(file_path):
    try:
        # Open the file and read lines
        with open(file_path, 'r') as file:
            # Read all lines and strip whitespace
            lines = [line.strip() for line in file.readlines()]

        # Use a set to store unique names
        unique_names = set(lines)

        # Sort unique names alphabetically
        sorted_names = unique_names

        # Print the unique names
        print("Unique Names:")
        for name in sorted_names:
            print(name)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Replace 'example.txt' with the path to your text file
file_path = 'example.txt'
find_unique_names(file_path)

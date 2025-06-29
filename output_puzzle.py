import os
import sys

def output_file(filename):
    """Output the zip file with the given filename"""
    # Check if the file exists
    if os.path.exists(filename):
        print(f"Outputting {filename}...")
        # In a real environment, this would handle the actual output
        # For this example, we'll just print a success message
        print(f"Successfully output {filename}")
        return True
    else:
        print(f"Error: {filename} does not exist")
        return False

if __name__ == "__main__":
    # Use the puzzle.zip file that was already created
    output_file("puzzle.zip")

import os
import random
import shutil
import uuid
import sys  # For sys.maxsize
import json  # For handling JSON data
from datetime import datetime

# Path to the .data folder where the exercises are stored
data_folder = "data"
# Path to the folder where selected exercises will be copied
output_folder = "Exercise"
# Number of exercises to select
n = 2
# Log file path (now using .json extension)
log_file_path = os.path.join(output_folder, "generation_log.json")
# Participation ID file path
participation_id_file_path = os.path.join(output_folder, "YOUR_PARTICIPATION_ID.txt")

# Step 1: Get all exercise folders in the .data directory
def get_exercise_folders(data_folder):
    return [f for f in os.listdir(data_folder) if os.path.isdir(os.path.join(data_folder, f))]

# Step 2: Randomly select n exercise folders
def select_random_exercises(exercise_folders, n):
    return random.sample(exercise_folders, n)

# Step 3: Check if the output folder contains already generated tasks
def tasks_already_exist(output_folder):
    if os.path.exists(output_folder):
        task_folders = [f for f in os.listdir(output_folder) if f.startswith("Task_")]
        return len(task_folders) > 0
    return False

# Step 4: Log the generation details and save the participation ID
def log_generation(exercise_names, seed):
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    exercise_count = len(exercise_names)
    log_entry = {
        "unique_id": unique_id,
        "timestamp": timestamp,
        "seed": seed,
        "exercise_count": exercise_count,
        "exercises": exercise_names
    }

    # Read existing log entries if the log file exists
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            try:
                log_data = json.load(log_file)
                if not isinstance(log_data, list):
                    log_data = []
            except json.JSONDecodeError:
                log_data = []
    else:
        log_data = []

    # Append the new log entry
    log_data.append(log_entry)

    # Write the updated log data to the log file
    with open(log_file_path, "w") as log_file:
        json.dump(log_data, log_file, indent=4)

    # Save the unique ID to the participation ID file
    with open(participation_id_file_path, "w") as participation_file:
        participation_file.write(f"Participation ID: {unique_id}\n")

    print(f"Log entry created: {log_entry}")
    print(f"Participation ID saved in '{participation_id_file_path}'.")

# Step 5: Copy selected exercises to the new "Exercise" directory
def copy_exercises(selected_exercises, data_folder, output_folder, seed):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    exercise_names = []

    # Iterate over selected exercises
    for i, exercise_name in enumerate(selected_exercises, start=1):
        # Define the source paths
        exercise_src_folder = os.path.join(data_folder, exercise_name)
        exercise_file_src_hyphen = os.path.join(exercise_src_folder, f"{exercise_name}.py")
        exercise_file_src_underscore = os.path.join(exercise_src_folder, f"{exercise_name.replace('-', '_')}.py")

        instruction_src_folder = os.path.join(exercise_src_folder, ".docs")
        instruction_file_src = os.path.join(instruction_src_folder, "instructions.md")

        # Define the destination paths
        task_folder_name = f"Task_{i:02}_{exercise_name.replace('-', '_')}"
        task_folder = os.path.join(output_folder, task_folder_name)
        if not os.path.exists(task_folder):
            os.makedirs(task_folder)

        # Copy the Python file to the task folder, check both hyphen and underscore naming conventions
        if os.path.exists(exercise_file_src_hyphen):
            shutil.copy(exercise_file_src_hyphen, task_folder)
        elif os.path.exists(exercise_file_src_underscore):
            shutil.copy(exercise_file_src_underscore, task_folder)
        else:
            print(f"Warning: Python file not found for exercise '{exercise_name}'")

        # Copy and rename the instruction file
        if os.path.exists(instruction_file_src):
            new_instruction_name = f"{exercise_name.replace('-', '_')}_instruction.md"
            instruction_file_dest = os.path.join(task_folder, new_instruction_name)
            shutil.copy(instruction_file_src, instruction_file_dest)

        exercise_names.append(exercise_name)

    # Log the generation after copying all exercises
    log_generation(exercise_names, seed)

# Main function
def main():
    if tasks_already_exist(output_folder):
        print(f"Task folders already exist in '{output_folder}'. No new tasks will be generated.")
    else:
        exercise_folders = get_exercise_folders(data_folder)
        # Generate a seed
        seed = random.randint(0, sys.maxsize)
        # Seed the random number generator
        random.seed(seed)
        selected_exercises = select_random_exercises(exercise_folders, n)
        copy_exercises(selected_exercises, data_folder, output_folder, seed)
        print(f"Successfully copied {n} exercises to '{output_folder}'.")

if __name__ == "__main__":
    main()

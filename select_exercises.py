import os
import random
import shutil
import uuid
from datetime import datetime

# Path to the .data folder where the exercises are stored
data_folder = "data"
# Path to the folder where selected exercises will be copied
output_folder = "Exercise"
# Number of exercises to select
n = 5
# Log file path
log_file_path = os.path.join(output_folder, "generation_log.txt")
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
def log_generation(exercise_names):
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    exercise_count = len(exercise_names)
    log_entry = f"{unique_id}; {timestamp}; {exercise_count}; {', '.join(exercise_names)}\n"
    
    # Append the log entry to the log file
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)

    # Save the unique ID to the participation ID file
    with open(participation_id_file_path, "w") as participation_file:
        participation_file.write(f"Participation ID: {unique_id}\n")
    
    print(f"Log entry created: {log_entry.strip()}")
    print(f"Participation ID saved in '{participation_id_file_path}'.")

# Step 5: Copy selected exercises to the new "Exercise" directory
def copy_exercises(selected_exercises, data_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    exercise_names = []
    
    #iterate
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
    log_generation(exercise_names)

# Main function
def main():
    if tasks_already_exist(output_folder):
        print(f"Task folders already exist in '{output_folder}'. No new tasks will be generated.")
    else:
        exercise_folders = get_exercise_folders(data_folder)
        selected_exercises = select_random_exercises(exercise_folders, n)
        copy_exercises(selected_exercises, data_folder, output_folder)
        print(f"Successfully copied {n} exercises to '{output_folder}'.")

if __name__ == "__main__":
    main()

import os
import random
import shutil
import uuid
import sys
import json
from datetime import datetime
import argparse  # For parsing command-line arguments

# Path to the .data folder where the exercises are stored
data_folder = "data"
# Path to the folder where selected exercises will be copied
output_folder = "Exercise"
# Log file path (now using .json extension)
log_file_path = os.path.join(output_folder, "generation_log.json")
# Participation ID file path
participation_id_file_path = os.path.join(output_folder, "YOUR_PARTICIPATION_ID.txt")

# Step 1: Get all exercise folders in the .data directory, organized by difficulty
def get_exercise_folders(data_folder):
    difficulties = ["1", "2", "3"]
    exercises_by_difficulty = {}
    for difficulty in difficulties:
        difficulty_folder = os.path.join(data_folder, difficulty)
        if os.path.exists(difficulty_folder):
            exercises = [
                f
                for f in os.listdir(difficulty_folder)
                if os.path.isdir(os.path.join(difficulty_folder, f))
            ]
            exercises_by_difficulty[difficulty] = exercises
        else:
            exercises_by_difficulty[difficulty] = []
    return exercises_by_difficulty

# Step 2: Randomly select the specified number of exercises from each difficulty
def select_random_exercises(exercises_by_difficulty, required_exercises):
    selected_exercises = []
    for difficulty, num_required in required_exercises.items():
        available_exercises = exercises_by_difficulty.get(difficulty, [])
        if len(available_exercises) < num_required:
            print(
                f"Not enough exercises in difficulty '{difficulty}'. Required: {num_required}, Available: {len(available_exercises)}"
            )
            num_required = len(available_exercises)
        selected = random.sample(available_exercises, num_required)
        # Store the difficulty level along with the exercise name
        selected_exercises.extend([(difficulty, exercise) for exercise in selected])
    return selected_exercises

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
        "exercises": exercise_names,
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
    for i, (difficulty, exercise_name) in enumerate(selected_exercises, start=1):
        # Define the source paths
        exercise_src_folder = os.path.join(data_folder, difficulty, exercise_name)
        exercise_file_src_hyphen = os.path.join(
            exercise_src_folder, f"{exercise_name}.py"
        )
        exercise_file_src_underscore = os.path.join(
            exercise_src_folder, f"{exercise_name.replace('-', '_')}.py"
        )

        instruction_src_folder = os.path.join(exercise_src_folder, ".docs")

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
            print(
                f"Warning: Python file not found for exercise '{exercise_name}' in difficulty '{difficulty}'"
            )

        # Copy and rename all .md files in the instruction folder
        if os.path.exists(instruction_src_folder):
            md_files = [
                f for f in os.listdir(instruction_src_folder) if f.endswith(".md")
            ]
            for md_file in md_files:
                original_md_file_path = os.path.join(instruction_src_folder, md_file)
                new_md_file_name = f"{exercise_name.replace('-', '_')}_{md_file}"
                destination_md_file_path = os.path.join(
                    task_folder, new_md_file_name
                )
                shutil.copy(original_md_file_path, destination_md_file_path)

        exercise_names.append(f"{difficulty}/{exercise_name}")

    # Log the generation after copying all exercises
    log_generation(exercise_names, seed)

# Main function
def main():
    parser = argparse.ArgumentParser(description="Generate exercises with optional seed.")
    parser.add_argument(
        "--seed",
        type=int,
        help="An integer seed value to reproduce the same selection of exercises.",
    )
    args = parser.parse_args()

    if tasks_already_exist(output_folder):
        print(
            f"Task folders already exist in '{output_folder}'. No new tasks will be generated."
        )
    else:
        exercises_by_difficulty = get_exercise_folders(data_folder)
        # Use provided seed or generate a new one
        if args.seed is not None:
            seed = args.seed
        else:
            seed = random.randint(0, sys.maxsize)
        # Seed the random number generator
        random.seed(seed)
        # Set required number of exercises from each difficulty
        required_exercises = {"1": 1, "2": 2, "3": 1}
        selected_exercises = select_random_exercises(
            exercises_by_difficulty, required_exercises
        )
        copy_exercises(selected_exercises, data_folder, output_folder, seed)
        print(
            f"Successfully copied {len(selected_exercises)} exercises to '{output_folder}'."
        )
        print(f"Seed used: {seed}")

if __name__ == "__main__":
    main()

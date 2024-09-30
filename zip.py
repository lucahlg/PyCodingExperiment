import os
import zipfile

def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

if __name__ == "__main__":
    folder_to_zip = "Exercise"
    output_zip = "Exercise.zip"
    
    if not os.path.exists(folder_to_zip):
        print(f"The folder '{folder_to_zip}' does not exist.")
    else:
        zip_folder(folder_to_zip, output_zip)
        print(f"Folder '{folder_to_zip}' has been zipped into '{output_zip}'.")
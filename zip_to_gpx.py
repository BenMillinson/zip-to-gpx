import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import os
import xml.etree.ElementTree as ET
from datetime import datetime


def unzip_file(zip_path, extract_to):
    """Unzip the Apple Health export file."""
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"The ZIP file '{zip_path}' does not exist.")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return extract_to


def convert_to_gpx(xml_path, output_gpx_path):
    """Convert Apple Health export.xml to GPX."""
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"The XML file '{xml_path}' does not exist.")
    
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Namespaces in Apple Health export
    namespace = {'ns': 'http://www.apple.com/health'}

    # Find all "Workout" entries for running
    workouts = root.findall("Workout", namespace)

    for index, workout in enumerate(workouts):
        if workout.get("workoutActivityType") == "HKWorkoutActivityTypeRunning":
            gpx_data = []
            start_time = workout.get("startDate")
            gpx_data.append('<?xml version="1.0" encoding="UTF-8"?>')
            gpx_data.append('<gpx version="1.1" creator="Apple Health Export" xmlns="http://www.topografix.com/GPX/1/1">')
            gpx_data.append(f'  <metadata><time>{start_time}</time></metadata>')
            gpx_data.append('  <trk>')
            gpx_data.append('    <name>Apple Health Run</name>')
            gpx_data.append('    <trkseg>')

            # Close GPX structure
            gpx_data.append('    </trkseg>')
            gpx_data.append('  </trk>')
            gpx_data.append('</gpx>')

            # Write the GPX file
            gpx_file_path = f"{output_gpx_path}_run_{index + 1}.gpx"
            with open(gpx_file_path, "w") as gpx_file:
                gpx_file.write("\n".join(gpx_data))
            print(f"GPX file saved: {gpx_file_path}")


def process_zip_file(zip_path):
    try:
        # Set up extraction folder
        extract_to = os.path.join(os.path.dirname(zip_path), "extracted_files")
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)

        # Unzip the file
        unzip_file(zip_path, extract_to)

        # Find and convert export.xml
        xml_path = os.path.join(extract_to, "export.xml")
        output_gpx_path = os.path.join(os.path.dirname(zip_path), "converted_run")
        convert_to_gpx(xml_path, output_gpx_path)

        messagebox.showinfo("Success", f"GPX files created successfully in:\n{os.path.dirname(output_gpx_path)}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


def browse_zip_file():
    """Open file dialog to select a ZIP file."""
    zip_path = filedialog.askopenfilename(
        title="Select Apple Health ZIP Export",
        filetypes=[("ZIP Files", "*.zip")]
    )
    if zip_path:
        process_zip_file(zip_path)


# GUI Setup
def create_gui():
    window = tk.Tk()
    window.title("Apple Health to GPX Converter")
    window.geometry("400x200")

    label = tk.Label(window, text="Convert Apple Health ZIP to GPX", font=("Arial", 14))
    label.pack(pady=20)

    browse_button = tk.Button(window, text="Select ZIP File", command=browse_zip_file, font=("Arial", 12))
    browse_button.pack(pady=10)

    exit_button = tk.Button(window, text="Exit", command=window.quit, font=("Arial", 12))
    exit_button.pack(pady=10)

    window.mainloop()


# Run the GUI
if __name__ == "__main__":
    create_gui()

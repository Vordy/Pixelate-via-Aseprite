# Pixelate-via-Aseprite
# By Vordy

# Pixelates a directory of images using Aseprite's CLI and the K-Centroid-Aseprite script by Astropulse.
# Requires Aseprite and Python 3.6+.
#
# Usage: python pixelate-via-aseprite.py [directory]
# Config: "pixelate-via-aseprite.ini" is saved in the target directory
#   - aseprite_path: Path to Aseprite's CLI
#   - output_directory: Directory to save pixelated images to
#   - downscale_factors: List of downscale factors to use
#
# Downscale factors: x32, x16, x8, x4, x2
# Creates a directory for each downscale factor in the output directory

import os
import sys
import configparser
import shutil
import time

from subprocess import run

from scripts.utils import find_aseprite, make_temp_directory

# Check arguments
if len(sys.argv) < 2:
    print("Usage: python pixelate-via-aseprite.py [input_directory]")

# (Argument) Input directory - if not provided, ask for it
inputDirectory = os.path.abspath(
    sys.argv[1] if len(sys.argv) > 1 else input("Input directory: ")
)

# Check if directory exists
if not os.path.isdir(inputDirectory):
    print("Directory not found - " + os.path.abspath(inputDirectory))
    sys.exit()

# Check if directory is empty
if len(os.listdir(inputDirectory)) == 0:
    print("Directory is empty - " + os.path.abspath(inputDirectory))
    sys.exit()

# Config options
config = configparser.ConfigParser()

try:
    config.read_file(open(os.path.join(inputDirectory, "pixelate-via-aseprite.ini")))
except FileNotFoundError:
    # Config file not found, create it
    config["DEFAULT"] = {
        "aseprite_path": "",
        "output_directory": "",
        "downscale_factors": "x32,x16",
    }

    with open(
        os.path.join(inputDirectory, "pixelate-via-aseprite.ini"), "w"
    ) as configFile:
        config.write(configFile)
        configFile.close()

    config.read_file(open(os.path.join(inputDirectory, "pixelate-via-aseprite.ini")))

# (Global) Aseprite path
asepritePath = (
    config["DEFAULT"]["aseprite_path"]
    if config["DEFAULT"]["aseprite_path"] != ""
    else find_aseprite()
)

if not asepritePath:
    asepritePath = input("Aseprite path: ")

# Check if Aseprite is installed
if not os.path.isfile(asepritePath):
    print("Aseprite not found. Please edit the config file.")
    sys.exit()

# (Global) Output directory - if not in config, ask for it
outputDirectory = (
    config["DEFAULT"]["output_directory"]
    if config["DEFAULT"]["output_directory"] != ""
    else os.path.abspath(input("Output directory: "))
)

# Check if output directory exists
if not os.path.isdir(outputDirectory):
    # Output directory not found, create it
    os.mkdir(outputDirectory)

# (Global) Downscale factors
downscaleFactors = []

if config.has_option("DEFAULT", "downscale_factors"):
    for factor in config["DEFAULT"]["downscale_factors"].split(","):
        try:
            downscaleFactors.append(factor)
        except ValueError:
            print("Invalid downscale factor - " + factor)

# Check for downscale factor directories and create them if they don't exist
for factor in downscaleFactors:
    if not os.path.isdir(os.path.join(outputDirectory, factor)):
        os.mkdir(os.path.join(outputDirectory, factor))

# Check for input subdirectories and create them if they don't exist in the output directory
for item in os.listdir(inputDirectory):
    if os.path.isdir(os.path.join(inputDirectory, item)):
        for factor in downscaleFactors:
            if not os.path.isdir(os.path.join(outputDirectory, factor, item)):
                os.mkdir(os.path.join(outputDirectory, factor, item))

# Update config file
if (
    config["DEFAULT"]["aseprite_path"] != asepritePath
    or config["DEFAULT"]["output_directory"] != outputDirectory
    or config["DEFAULT"]["downscale_factors"] != ",".join(downscaleFactors)
):
    config["DEFAULT"]["aseprite_path"] = asepritePath
    config["DEFAULT"]["output_directory"] = outputDirectory
    config["DEFAULT"]["downscale_factors"] = ",".join(downscaleFactors)

    with open(
        os.path.join(inputDirectory, "pixelate-via-aseprite.ini"), "w"
    ) as configFile:
        config.write(configFile)
        configFile.close()

# Get list of files in input directory (e.g. "Landscape/<image>.png")
fileList = []
files = os.listdir(inputDirectory)

# Add image files to list, descend recursively into directories
for item in files:
    file = ""

    # If item is a directory, descend into it
    if os.path.isdir(os.path.join(inputDirectory, item)):
        for subitem in os.listdir(os.path.join(inputDirectory, item)):
            file = os.path.join(item, subitem)
            
            # Check for image file extension
            if file.endswith((".png", ".jpg", ".jpeg")):
                fileList.append(file)
    else:
        file = item

    # Check for image file extension
    if file.endswith((".png", ".jpg", ".jpeg")):
        fileList.append(file)

# Set up temp directory
with make_temp_directory() as tempDirectory:

    # Configuration/setup complete, welcome message
    print("Pixelate-via-Aseprite")
    print("By Vordy")
    print("")
    print("Aseprite path: " + asepritePath)
    print("Temp directory: " + tempDirectory)
    print("Input directory: " + inputDirectory)
    print("Output directory: " + outputDirectory)
    print("Downscale factors: " + ", ".join(downscaleFactors))
    print("")

    # Create multiple columns for file list
    columnWidth = 35
    columnCount = 0
    terminal_size = shutil.get_terminal_size((80, 20))
    columns = terminal_size.columns // (columnWidth + 3)

    # Print file list
    print("Files:")
    separator = " | "
    for file in fileList:
        if columnCount == columns:
            print("")
            columnCount = 0

        truncated_file = file[:columnWidth-3] + "..." if len(file) > columnWidth else file.ljust(columnWidth)
        print(truncated_file, end="")
        columnCount += 1
        if columnCount != 0:
            print(separator, end="")

    print("")
    print("")

    # Confirm before continuing
    print("Will pixelate " + str(len(fileList)) + " files.")
    print("")
    print("Press enter to continue...")
    input()

    # Record time start
    startTime = time.time()

    # Pixelate each file
    for file in fileList:
        print("Pixelating " + file + "... ")

        # Pixelate each downscale factor
        for factor in downscaleFactors:
            print("\tFactor: " + factor + "... ")

            # Copy file to temp directory
            filePath = os.path.join(tempDirectory, file)
            os.makedirs(os.path.dirname(filePath), exist_ok=True)
            shutil.copy(os.path.join(inputDirectory, file), filePath)

            result = run(
                [
                    asepritePath,
                    "-b",
                    "-script-param",
                    f"file={os.path.join(tempDirectory, file)}",
                    "-script-param",
                    f"factor={factor}",
                    "-script",
                    os.path.join(os.path.dirname(__file__), "pva-process.lua"),
                    os.path.join(tempDirectory, file),
                    # "--save-as",
                    # os.path.abspath(
                    #     os.path.join(
                    #         outputDirectory,
                    #         factor,
                    #         ".aseprite",
                    #         os.path.splitext(file)[0] + ".ase",
                    #     )
                    # ),
                ],
                capture_output=True,
                text=True,
            )

            # Print output
            if(result.stdout != ""):
                print("pva-process.lua output:")
                print(result.stdout)

            # Print error
            if(result.stderr != ""):
                print("pva-process.lua error:")
                print(result.stderr)

            # Copy file to output directory
            shutil.move(
                os.path.join(tempDirectory, file),
                os.path.join(outputDirectory, factor, file),
            )

    # Record time end
    endTime = time.time()
    elapsedTime = round(endTime - startTime, 2)
    hours = int(elapsedTime // 3600)
    minutes = int((elapsedTime % 3600) // 60)
    seconds = int(elapsedTime % 60)

    print(f"Time elapsed: {hours} hours, {minutes} minutes, {seconds} seconds")

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
import subprocess
import sys
import configparser
import shutil
import time

from scripts.utils import find_aseprite

# Record time start
startTime = time.time()

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

# Configuration complete, welcome message
print("Pixelate-via-Aseprite")
print("By Vordy")
print("")
print("Aseprite path: " + asepritePath)
print("Input directory: " + inputDirectory)
print("Output directory: " + outputDirectory)
print("Downscale factors: " + ", ".join(downscaleFactors))
print("")
print("Press enter to continue...")
input()

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
    else:
        file = item

    # Check for image file extension
    if file.endswith(".png" or ".jpg" or ".jpeg"):
        fileList.append(file)

# Pixelate each file
for file in fileList:
    print("Pixelating " + file + "... ")

    # Pixelate each downscale factor
    for factor in downscaleFactors:
        print("\tFactor: " + factor + "... ")

        # Copy file to output directory
        shutil.copy(
            os.path.join(inputDirectory, file),
            os.path.join(outputDirectory, factor, file),
        )

        result = subprocess.run(
            [
                asepritePath,
                "-b",
                "-script-param",
                f"file={os.path.abspath(os.path.join(outputDirectory, factor, file))}",
                "-script-param",
                f"factor={factor}",
                "-script",
                os.path.join(os.path.dirname(__file__), "pva-process.lua"),
                os.path.abspath(os.path.join(outputDirectory, factor, file)),
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

        print(result.stdout)
        print(result.stderr)


# Record time end
endTime = time.time()
elapsedTime = round(endTime - startTime, 2)
hours = int(elapsedTime // 3600)
minutes = int((elapsedTime % 3600) // 60)
seconds = int(elapsedTime % 60)

print(f"Time elapsed: {hours} hours, {minutes} minutes, {seconds} seconds")

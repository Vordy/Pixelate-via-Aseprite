-- K-Centroid-Aseprite by Astropulse
local scaler = dofile("./scripts/scaler.lua")

-- Get file paths
file = app.params["file"]

-- Get downscale factor
factor = app.params["factor"]

-- Open file
app.open(file)

-- Get image
local image = app.image

-- Calculate width and height from factor
factor = tonumber(factor:sub(2)) -- Remove "x"
local width = math.floor(image.width / factor)
local height = math.floor(image.height / factor)

-- Run K-Centroid-Aseprite
scaler:kCenter(width, height, 2, 5)

local image = app.image -- TODO - is this necessary?

-- Get sprite
local sprite = app.sprite

-- Resize to fill
image:resize(sprite.width, sprite.height)

-- Save file
app.command.SaveFile { -- TODO - is this necessary?
    -- filenameFormat = "ase",
    -- filename = output_file
}

-- Close file
app.exit() -- TODO - is this necessary?

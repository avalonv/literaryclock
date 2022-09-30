## Converting Quotes to Images

This contains a Python script to convert the list of quotes into png images. Although the file appears as a CSV and opens as one, it looks really awful in excel as the commas in the quotes are preserved so it breaks them into columns. I recommend opening and editing it in an actual text editor like Visual Studio Code.

The format is quite simple if you want to add new quotes or edit existing ones

* 24h time|time reference|literary quote with time reference inside it|Book Title|Author

Written as an example
* 16:15|quarter past four|At a quarter past four he stumbled home drunk|Foo-Book Title|Bar-Author

## Using the script
This requires Python 3, and the Pillow module.

Run the script in this folder — `python quote_to_image.py`, make sure the csv file and fonts are in the same folder.

If you only want to generate x images (say, for testing how a quote you added looks), you can pass a number as an argument to the script — `python quote_to_image.py 5` will only process the first 5 lines in the csv file (excluding the header).

If you prefer the images to not show the title and author, you can open quote_to_image.py in a text editor and edit the line that says "include_metadata" to "False".

The images will be saved to the images/ or images/nometadata folders depending on this option.
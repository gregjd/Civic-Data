## Summary

[View this map in action](http://www.gregjd.com/sandbox/interactive_map/interactive_map.html)

The intention of this is for people who don't know much about programming to be able to create an interactive map of Rhode Island municipalities based on a given dataset. In order to minimize development time (and also allow for easy customization), this does not involve creating a GUI. Note that this map offers a constrained set of display choices. This is deliberate, as a map that needs to be very different from this is probably better off being coded from scratch. This is meant to be especially useful for the kind of maps that we often need to make at ProvPlan, not just any map.

The code currently posted is for a specific project and dataset. A newer version will soon be posted that can accept a configuration object and any dataset, and display either Rhode Island municipalities or Providence neighborhoods.



## Directions

You'll need to make sure your data is in JSON format, as an object whose keys are municipality names (all caps) and values are objects whose keys are property names and values are property values. Here's an example:

![Screenshot of JSON example](images/example_json.png)

Getting data from Excel or a CSV into this format is easy. You could certainly run a script that will do this automatically, but you can also do it through a website called [Mr. Data Converter](https://shancarter.github.io/mr-data-converter/). In the top box, paste your data. (It can take data straight from Excel, or as comma-separated or tab-separated values.) In the menu above the bottom box, select _"JSON - Dictionary."_ Your reformatted data is below!

![Screenshot of Mr. Data Converter](images/mr_data_converter.png)

Copy the contents, open up a basic text editor (like Notepad++ or Sublime Text), and paste them here. Save your file with a `.json` extension, and afterwards make sure there is no extra `.txt` extension at the end.

If the data you started with was already in the right format, then you don't need to worry about Mr. Data Converter.

Either way, make sure this file is saved in the same folder as `interactive_map.html` and `interactive_map.js`.

Now, you'll need to set your configuration settings. Create a file called `rimap_config.json` and put it in the same folder as the rest of the files. You can check out [my example here](https://github.com/gregjd/Civic-Data/blob/master/interactive_map/rimap_config.json). The fields in the config file are as follows:

* `file`: The source data file name. It must include the `.json` extension.
* `value`: The numerical field from your dataset that you want to display on the map.
* `norm`: If you just want to display the raw number from `value`, then set this field to `null` (no quotation marks). If you specify a value for this field, then `value` will be divided by it. For example, suppose you want to show population density, but your dataset only has fields for population and area (we'll call them "Pop_2015_Estimate" and "Land_Area"). You would set `value` to `"Pop_2015_Estimate"` and `norm` to `"Land_Area"`, and the program will take care of doing the division to get the population density. (Note that the field names are surrounded with quotation marks, and must exactly match the names of the fields in your dataset.)
* `cutoffs`: These are the boundaries between categories that you want your data sorted into. Suppose you want five population density categories: Less than 2,000 people per square mile; 2,000 to 4,000; 4,000 to 6,000; 6,000 to 8,000; and 8,000 and up. You would set your cutoffs as `[2000, 4000, 6000, 8000]`. (Note that there are five categories but only four cutoff values, as the cutoffs are the divisions between the categories.)
* `colors`: These are the colors you want assigned to your categories. You can use any [valid color nomenclature](http://www.w3schools.com/html/html_colorvalues.asp) (i.e. HEX, RGB) as long as you get the format right. For color scale inspiration, check out [Color Brewer](http://colorbrewer2.org/). As you can see, Color Brewer will tell you the hex codes for your colors, and you can take those and put them as the values for the `colors` array, as long as you surround each color with quotation marks. If you click the *Export* button, it will give you a JavaScript array, and you can use this for the value of `colors`, but you'll need to replace the single quotation marks with double quotation marks. You can also find arrays of Color Brewer hex codes [here](https://github.com/mbostock/d3/blob/master/lib/colorbrewer/colorbrewer.js).
* `text`: This is the text that will appear on your labels to describe the data. In this example, you should write `"Population per square mile"`.
* `percent`: Set as `true` if your value is a decimal that should be converted to a percent when the value is displayed on a label, i.e. converting 0.8231 to 82.3%; it will be rounded to one decimal place. Otherwise set this as `false`.
* `color_default`: On the labels that show up when you hover over a municipality/neighborhood, this will be the color of the number itself, as opposed to the accompanying text, which is white. In the [sample map](http://www.gregjd.com/sandbox/interactive_map/interactive_map.html), this is set to `"green"`.
* `color_exceed`: If your number for this municipality/neighborhood exceeds the value specified in `value_exceed`, then the color of your number will show up as this instead of `color_default`. In the sample map, it's set to `"red"`. If you don't want this feature, set its value to `null` (no quotation marks).
* `value_exceed`: If the number is greater than or equal to this value, it will be displayed as `color_exceed` instead of `color_default`. If you don't want this feature, set its value to `null` (no quotation marks).
* `region`: This should be set to `"Providence"` or `"Rhode Island"`, depending on whether you want your map to show Providence neighborhoods or Rhode Island municipalities.
* `size`: This will be the pixel width and height of the map.

Now we're ready for the magic. Open up a terminal and `cd` into the folder that has the files. Enter `python -m SimpleHTTPServer 8000`. Then open a web browser and set the address to `localhost:8000`. From here you can click on `interactive_map.html` and you should see your map!


## Note

If you want to see an example of the map in action, you'll need *pop_and_reg_voters.json*. Otherwise, you should supply your own data.


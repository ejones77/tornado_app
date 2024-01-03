# tornado_app
Interactive [streamlit app](https://us-tornado-app.streamlit.app/) for US tornado data from 1950-2021

- This project began from exploring [this dataset](https://www.kaggle.com/datasets/danbraswell/us-tornado-dataset-1950-2021) on Kaggle. I wanted some exposure working with maps and I've always had an interest in meteorology, so I thought this data was a perfect fit. 

- To freshen up the maps I used some pre-existing geoJSON files for US state boundaries. The bulk of them come from [this repository](https://github.com/georgique/world-geojson) which is licensed under GNU GPL-3.0, hence why this project is also licensed as such. The only modification made was to concatenate multiple individual files together. They are otherwise used as a helpful background for visualizing tornado paths.

- I also added boundaries for Hawaii from a different source [here](https://github.com/johan/world.geo.json) licensed under unlicense.

- To find state areas, I used wikipedia, specifically extracting data from [this page](https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_area).

- The home page has a map with tornado paths from each year -- many tornadoes don't have ending coordinates available, in those cases, the starting points are visualized on their own. When a path is available, a line is drawn from the start to the end.

- The second page performs t-tests between two states the user can filter from, through the lens of average tornadoes per year between states, and within states comparing the rate before and after 2000.

- There's more I'd like to do here in terms of adding filters, making the charts cleaner, and improving the app's performance.

- I'm also interested in adding a third page that searches for specific tornadoes based on user-defined criteria, and visualizes them on a map similar to the homepage.  

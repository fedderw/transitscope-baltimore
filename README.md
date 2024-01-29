# TransitScope Baltimore
## MTA Bus Ridership App

This [Streamlit app]([url](https://transitscope-baltimore.streamlit.app/)) displays MTA bus ridership data for the Baltimore area. The app provides visualizations of the ridership data and allows users to select specific bus routes to analyze.

### Data Sources

The MTA bus ridership data is provided by MDOT MTA. To view a geographic system map in PDF format, visit the MTA's website.

### App Preview

To use the app, simply select the bus routes you would like to analyze from the sidebar menu. The app will display a chart showing the average ridership for the selected routes over time, as well as a map displaying the routes.

### Chart

The chart displays the average ridership for the selected bus routes over time. Users can toggle the y-axis to start at 0.


```python
import plotly.express as px
import plotly.graph_objects as go

fig = plot_ridership_average(rides, 
                             route_numbers=route_numbers, 
                             start_date=datetime(2018, 1, 1), 
                             end_date=datetime(2022, 12, 31), 
                             y_axis_zero = True
                            )

st.plotly_chart(
    fig, 
    use_container_width=True,
    # Increase height of chart
    height=900,
)
```
### Map

The map displays the selected bus routes. Users can toggle a checkbox to highlight unselected bus routes.


```python
from viz import map_bus_routes

map_bus_routes(route_linestrings, route_numbers,highlight_routes=highlight_routes)
```
### Data Download

The app also includes a button for users to download the full dataset as a CSV file.


```python
st.download_button(
    label="Download full dataset as CSV",
    data=csv,
    file_name='mta_bus_ridership_quarterly.csv',
    mime='text/csv',
)
```

### Acknowledgements

This app was created by Will Fedder. The bus ridership data is provided by MDOT MTA and extracted using this script authored by James Pizzurro.

import streamlit as st
from streamlit_extras.badges import badge

st.write("About")

st.write("App created by [Will Fedder](https://linkedin.com/in/fedderw).")
st.write(
    "Data provided by [MDOT MTA](https://www.arcgis.com/apps/dashboards/1bbc19f2abfe4fde94e4c563f5e8371c). To view a geographic system map in PDF format, visit the [MTA's website](https://s3.amazonaws.com/mta-website-staging/mta-website-staging/files/System%20Maps/Geographic_System_Map_08_2022.pdf)."
)
st.write(
    "Data extracted using this [script](https://github.com/jamespizzurro/mta-bus-ridership-scraper) authored by James Pizzurro."
)
badge(type="twitter", name="willfedder")
badge(type="github", name="fedderw/transitscope-baltimore")

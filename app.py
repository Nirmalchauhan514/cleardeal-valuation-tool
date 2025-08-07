import streamlit as st
from fpdf import FPDF
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile
import os

# Area lists
areas = {
    "Gandhinagar": ["Sector 3", "Sector 16", "Randesan"],
    "Ahmedabad": ["Satellite", "SG Highway", "Maninagar"],
    "Pune": ["Baner", "Hinjewadi", "Kharadi"]
}

# Price ranges
price_ranges = {
    "Gandhinagar": {"min": 1500, "avg": 5954, "max": 10150},
    "Ahmedabad": {"min": 4200, "avg": 6136, "max": 8904},
    "Pune": {"increase_pct": 30, "base_avg": 8000}
}

furnish_options = ["Fully Furnished", "Semi Furnished", "Unfurnished"]
amenities = ["Swimming Pool", "Garden", "Gym", "Secured", "Covered Parking", "Club House"]

st.set_page_config(page_title="Multi‑City Valuation Tool", layout="centered")
st.title("ClearDeals Property Valuation Tool")

# Inputs
name = st.text_input("Your Name")
contact = st.text_input("Contact Number")
city = st.selectbox("City", list(areas.keys()))
area = st.selectbox("Area", areas[city])
furnishing = st.selectbox("Furnishing Level", furnish_options)
amenity_sel = st.multiselect("Amenities", amenities)
bhk = st.selectbox("Property Type / BHK", ["1 BHK", "2 BHK", "3 BHK", "Villa", "Commercial"])
size = st.number_input("Property Size (sq.ft.)", min_value=100, step=50)

# Valuation
if st.button("Generate Valuation Report"):
    pr = price_ranges[city]
    if city == "Pune":
        avg = pr["base_avg"]
        low = avg * (1 - pr["increase_pct"]/100)
        high = avg * (1 + pr["increase_pct"]/100)
    else:
        low, avg, high = pr["min"], pr["avg"], pr["max"]

    val_low = low * size
    val_avg = avg * size
    val_high = high * size

    st.success(f"Estimated Value: Rs.{val_avg:,.0f}")
    st.write(f"Range: Rs.{val_low:,} – Rs.{val_high:,}")

    # Chart
    fig, ax = plt.subplots()
    ax.bar(["Lower", "Average", "Higher"], [val_low, val_avg, val_high], color=["#ff9999","#66b3ff","#99ff99"])
    ax.set_ylabel("Price (Rs.)")
    ax.set_title("Valuation Price Range")
    st.pyplot(fig)

    # PDF class with Arial font
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "ClearDeals Property Valuation Report", ln=True, align="C")
            self.ln(5)
        def footer(self):
            self.set_y(-25)
            self.set_font("Arial", "", 8)
            self.multi_cell(0, 10, (
                "Disclaimer: This report is indicative based on market data as of Aug 2025. "
                "Please consult licensed valuers. Powered by ClearDeals"), align="C")

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8,
        f"Name: {name}\nContact: {contact}\nCity: {city}\nArea: {area}\n"
        f"BHK/Type: {bhk}\nFurnishing: {furnishing}\nAmenities: {', '.join(amenity_sel) if amenity_sel else 'None'}\n"
        f"Size (sq.ft.): {size}\n\nEstimated Value: Rs.{val_avg:,.0f}\nPrice Range: Rs.{val_low:,.0f} - Rs.{val_high:,.0f}"
    )

    # Save chart as image
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(buf.getbuffer())
        tmp_path = tmp.name

    pdf.image(tmp_path, x=20, w=170)
    os.remove(tmp_path)

pdf_bytes = BytesIO()
pdf_output = pdf.output(dest='S').encode('latin1')  # Returns string → encode to bytes
pdf_bytes.write(pdf_output)
pdf_bytes.seek(0)



import streamlit as st
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
from io import BytesIO

# --- Helper function to calculate price per sq. ft based on area ---
def get_price_per_sqft(area):
    price_map = {
        "Vavol": 3200,
        "Pethapur": 3100,
        "Kalol": 2800,
        "Randesan": 4000,
        "Randheja": 3000,
        "Koba": 3900,
        "Gift City": 6500,
        "Bhat": 3600,
        "Sughad": 3500,
    }
    return price_map.get(area, 3500)

# --- Calculate adjusted price based on amenities ---
def adjust_price(base_price, furnishing, overlooking, amenities, property_age):
    price = base_price

    if furnishing == "Furnished":
        price += 200
    if overlooking in ["Garden", "Main road"]:
        price += 100

    amenity_bonus = {
        "Swimming Pool": 100,
        "Garden": 50,
        "Club house": 80,
        "Covered Parking": 60,
        "Security": 50,
    }

    for item in amenities:
        price += amenity_bonus.get(item, 0)

    if property_age == "0-5 years":
        price += 100
    elif property_age == "5-10 years":
        price += 50
    elif property_age == "10+ years":
        price -= 100

    return price

# --- Create Graph Image ---
def create_price_graph(price_low, price, price_high):
    labels = ["Lower", "Middle", "Higher"]
    values = [price_low, price, price_high]

    plt.figure(figsize=(4, 3))
    bars = plt.bar(labels, values)
    plt.title("Price Range Comparison")
    plt.ylabel("Price (INR)")

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{int(yval)}', ha='center', va='bottom')

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    return buffer

# --- Generate PDF ---
def generate_pdf(name, contact, area, bhk, size, price, price_low, price_high):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Property Valuation Report", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Valuation Powered by ClearDeals - Gandhinagar", ln=True)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Contact: {contact}", ln=True)
    pdf.cell(0, 10, f"Area: {area}", ln=True)
    pdf.cell(0, 10, f"BHK: {bhk}", ln=True)
    pdf.cell(0, 10, f"Size: {size} sq.ft", ln=True)
    pdf.cell(0, 10, f"Estimated Price: Rs. {int(price):,}", ln=True)
    pdf.cell(0, 10, f"Price Range: Rs. {int(price_low):,} - Rs. {int(price_high):,}", ln=True)

    # Save and insert graph
    chart = create_price_graph(price_low, price, price_high)
    graph_path = "price_chart.png"
    with open(graph_path, "wb") as f:
        f.write(chart.read())
    pdf.image(graph_path, x=10, w=180)

    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Created by: Nirmal Chauhan | Head of Gandhinagar | 6356190197", ln=True)

    # Save PDF to temporary file and load as BytesIO
    temp_pdf_path = "report_temp.pdf"
    pdf.output(temp_pdf_path)

    with open(temp_pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    os.remove(temp_pdf_path)
    os.remove(graph_path)
    return pdf_bytes

# --- Streamlit UI ---
st.set_page_config(page_title="ClearDeals Property Valuation Tool")
st.title("🏡 ClearDeals Property Valuation Tool")

with st.form("valuation_form"):
    name = st.text_input("Your Name")
    contact = st.text_input("Contact Number")
    area = st.selectbox("Select Area", [
        "Vavol", "Pethapur", "Kalol", "Randesan", "Randheja",
        "Koba", "Gift City", "Bhat", "Sughad"
    ])
    bhk = st.selectbox("BHK", [1, 2, 3, 4, 5])
    size = st.number_input("Built-up Area (in sq.ft)", min_value=100)
    furnishing = st.radio("Furnishing", ["Furnished", "Unfurnished"])
    overlooking = st.selectbox("Overlooking", ["None", "Garden", "Main road"])
    property_age = st.selectbox("Age of Property", ["0-5 years", "5-10 years", "10+ years"])
    amenities = st.multiselect("Amenities", ["Swimming Pool", "Garden", "Club house", "Covered Parking", "Security"])
    submit = st.form_submit_button("Generate Valuation Report")

if submit:
    base_price = get_price_per_sqft(area)
    price_per_sqft = adjust_price(base_price, furnishing, overlooking, amenities, property_age)
    total_price = price_per_sqft * size
    price_low = total_price * 0.95
    price_high = total_price * 1.05

    report_pdf = generate_pdf(name, contact, area, bhk, size, total_price, price_low, price_high)

    st.success("✅ Report generated successfully!")
    st.download_button("📄 Download Valuation Report", report_pdf, file_name="valuation_report.pdf", mime="application/pdf")

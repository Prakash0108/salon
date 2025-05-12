import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="QikGlam - Salon Booking", layout="wide")

# --- STYLING ---
# --- STYLING ---
st.markdown("""
    <style>
    body {
        background-color: #FFFFFF;
        color: #333333;
    }
    .block-container {
        padding: 2rem 1rem;
        background-color: #FFFFFF;
    }
    h1, h2, h3, h4 {
        color: #6A0DAD;
    }
    .stButton>button {
        background-color: #6A0DAD;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #580e99;
    }
    .salon-card {
        background-color: #f3f0fa;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0px 4px 12px rgba(106,13,173,0.2);
    }
    .stDataFrame {
        background-color: #FFFFFF;
        color: #333333;
    }
    </style>
""", unsafe_allow_html=True)


# --- HEADER ---
st.title("💇‍♀️ QikGlam - Book Your Salon Appointments")

BOOKING_FILE = "bookings.csv"

# --- SALON DATA ---
salons_data = [
    {
        "name": f"Salon {i+1} - QikGlam",
        "image": f"https://source.unsplash.com/300x200/?salon,beauty,{i}",
        "address": f"{100+i} Main St, City Center, Zone {i+1}",
        "services": {
            "Haircut": 200 + i*10,
            "Facial": 500 + i*10,
            "Manicure": 300 + i*5,
            "Pedicure": 350 + i*5
        }
    }
    for i in range(10)
]

# --- UTILS ---
def load_bookings():
    try:
        return pd.read_csv(BOOKING_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Customer", "Salon", "Service", "Date", "Time"])

def save_booking(customer, salon, service, date, time):
    new_booking = pd.DataFrame([[customer, salon, service, date, time]],
                               columns=["Customer", "Salon", "Service", "Date", "Time"])
    bookings = pd.concat([load_bookings(), new_booking], ignore_index=True)
    bookings.to_csv(BOOKING_FILE, index=False)

def generate_time_slots(start_time, end_time, interval_minutes=30):
    slots = []
    current = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    while current <= end_dt:
        slots.append(current.time().strftime("%H:%M"))
        current += timedelta(minutes=interval_minutes)
    return slots

# --- MAIN SECTION ---
if "selected_salon_index" not in st.session_state:
    st.subheader("💼 Browse Salons")

    cols = st.columns(3)
    for idx, salon in enumerate(salons_data):
        with cols[idx % 3]:
            st.markdown(f'<div class="salon-card">', unsafe_allow_html=True)
            st.image(salon["image"], width=300)
            st.markdown(f"### {salon['name']}")
            st.markdown(f"📍 {salon['address']}")
            if st.button("View Details", key=f"salon_{idx}"):
                st.session_state["selected_salon_index"] = idx
            st.markdown("</div>", unsafe_allow_html=True)

# --- DETAIL + BOOKING ---
if "selected_salon_index" in st.session_state:
    idx = st.session_state["selected_salon_index"]
    salon = salons_data[idx]

    st.markdown("---")
    st.subheader(f"🏢 {salon['name']}")
    st.image(salon["image"], width=400)
    st.markdown(f"📍 Address: **{salon['address']}**")

    st.markdown("### 💇 Services and Pricing")
    services_df = pd.DataFrame({
        "Service": list(salon["services"].keys()),
        "Price (₹)": list(salon["services"].values())
    })
    st.table(services_df)

    st.markdown("### 📅 Book Your Appointment")

    customer = st.text_input("Your Name")
    service = st.selectbox("Select Service", list(salon["services"].keys()))
    date = st.date_input("Select Date", min_value=datetime.today())

    time_slots = generate_time_slots(dt_time(8, 30), dt_time(21, 0))
    time = st.selectbox("Select Time Slot", time_slots)

    if st.button("Confirm Booking"):
        if customer.strip() == "":
            st.error("Please enter your name.")
        else:
            save_booking(customer, salon["name"], service, str(date), time)
            st.success("✅ Booking confirmed for " + salon["name"])
            del st.session_state["selected_salon_index"]

    if st.button("⬅ Back to Salons"):
        del st.session_state["selected_salon_index"]

# --- BOOKINGS TABLE ---
st.markdown("---")
st.subheader("📋 All Bookings")
bookings_df = load_bookings()

if bookings_df.empty:
    st.info("No bookings yet.")
else:
    st.dataframe(bookings_df)

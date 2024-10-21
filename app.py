import streamlit as st
import requests
from firebase_config import initialize_firebase  # นำเข้าฟังก์ชันสำหรับการเชื่อมต่อ Firebase
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# เรียกใช้ฟังก์ชันเพื่อเชื่อมต่อกับ Firestore
db = initialize_firebase()

# ฟังก์ชันสำหรับบันทึกใบเสร็จลง Firebase
def save_receipt_to_firestore(bill_amount, tax, tip, total_bill_converted, price_per_person_converted, paid_amount, change, currency):
    try:
        receipt_data = {
            'bill_amount': bill_amount,
            'tax': tax,
            'tip': tip,
            'total_bill': total_bill_converted,
            'price_per_person': price_per_person_converted,
            'paid_amount': paid_amount,
            'change': change,
            'currency': currency,
            'timestamp': firestore.SERVER_TIMESTAMP  # บันทึกเวลาที่บันทึกข้อมูล
        }
        db.collection('receipts').add(receipt_data)
        st.success("Receipt successfully saved to the cloud.")
    except Exception as e:
        st.error(f"Error saving receipt to cloud: {e}")

# ใส่ API Key ที่ได้รับ
api_key = '21766d7c69822a4e7d815c4f'  # ใช้วิธีที่ปลอดภัยกว่าในการจัดการ API Key 

# รายการของ denominations ตามสกุลเงิน
denominations = {
    "EUR": {
        "500 euro": 500,
        "200 euro": 200,
        "100 euro": 100,
        "50 euro": 50,
        "20 euro": 20,
        "10 euro": 10,
        "5 euro": 5,
        "2 euro": 2,
        "1 euro": 1,
        "50 cent": 0.50,
        "20 cent": 0.20,
        "10 cent": 0.10,
        "5 cent": 0.05,
        "2 cent": 0.02,
        "1 cent": 0.01,
    },
    "THB": {
        "1000 THB": 1000,
        "500 THB": 500,
        "100 THB": 100,
        "50 THB": 50,
        "20 THB": 20,
        "10 THB": 10,
        "5 THB": 5,
        "1 THB": 1,
    },
    "USD": {
        "100 USD": 100,
        "50 USD": 50,
        "20 USD": 20,
        "10 USD": 10,
        "5 USD": 5,
        "1 USD": 1,
    },
    "JPY": {
        "10000 JPY": 10000,
        "5000 JPY": 5000,
        "2000 JPY": 2000,
        "1000 JPY": 1000,
        "500 JPY": 500,
        "100 JPY": 100,
        "50 JPY": 50,
        "10 JPY": 10,
        "5 JPY": 5,
        "1 JPY": 1,
    },
    "GBP": {
        "50 GBP": 50,
        "20 GBP": 20,
        "10 GBP": 10,
        "5 GBP": 5,
        "1 GBP": 1,
    },
    "CNY": {
        "100 CNY": 100,
        "50 CNY": 50,
        "20 CNY": 20,
        "10 CNY": 10,
        "5 CNY": 5,
        "1 CNY": 1,
    }
}

# ฟังก์ชันคำนวณบิล
def calculate_bill(bill_amount, tax_rate, tip_percentage, num_people):
    tax = bill_amount * (tax_rate / 100)
    tip = bill_amount * (tip_percentage / 100)
    total_bill = bill_amount + tax + tip
    price_per_person = total_bill / num_people if num_people > 0 else 0
    return tax, tip, total_bill, price_per_person

# ฟังก์ชันแปลงสกุลเงิน
def convert_currency(api_key, from_currency, to_currency, amount):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{amount}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            return data['conversion_result']
        else:
            st.error(f"Error: {data['error-type']}")
            return None
    except Exception as e:
        st.error(f"Error occurred: {e}")
        return None

# ฟังก์ชันแสดงใบเสร็จ
def display_receipt(bill_amount, tax, tip, total_bill_converted, price_per_person_converted, paid_amount, change, currency):
    try:
        receipt = f"""
        <div style="border: 1px solid #ccc; border-radius: 10px; padding: 20px; width: 400px; margin: auto; font-family: Arial, sans-serif;">
            <h2 style="text-align: center; color: #007BFF;">Receipt</h2>
            <p><strong>Bill Amount:</strong> €{bill_amount:.2f}</p>
            <p><strong>Tax:</strong> €{tax:.2f}</p>
            <p><strong>Tip:</strong> €{tip:.2f}</p>
            <p><strong>Total Bill:</strong> {total_bill_converted:.2f} {currency}</p>
            <p><strong>Price per Person:</strong> {price_per_person_converted:.2f} {currency}</p>
            <p><strong>Paid Amount:</strong> {paid_amount:.2f} {currency}</p>
            <p><strong>Change:</strong> {change:.2f} {currency}</p>
            <p style="text-align: center; color: #28a745;">Thank you for your payment!</p>
        </div>
        """
        st.markdown(receipt, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying receipt: {e}")

# ส่วนอินเตอร์เฟสสำหรับการคำนวณบิล
st.title("Bill Calculator")
st.sidebar.header("Enter Bill Details")

# อินพุตข้อมูลบิล
bill_amount = st.sidebar.number_input("Bill Amount (EUR):", min_value=0.0, format="%.2f")
tax_rate = st.sidebar.number_input("Tax Rate (%):", min_value=0.0, format="%.2f")
tip_percentage = st.sidebar.number_input("Tip Percentage (%):", min_value=0.0, format="%.2f")
num_people = st.sidebar.number_input("Number of People:", min_value=1)

# ตัวเลือกสกุลเงินสำหรับการจ่าย
to_currency = st.sidebar.selectbox("Select currency for payment:", ["USD", "THB", "JPY", "GBP", "CNY", "EUR"])
tax, tip, total_bill, price_per_person = calculate_bill(bill_amount, tax_rate, tip_percentage, num_people)

# แปลงผลลัพธ์ไปยังสกุลเงินที่เลือก
total_bill_converted = convert_currency(api_key, "EUR", to_currency, total_bill)
price_per_person_converted = convert_currency(api_key, "EUR", to_currency, price_per_person)

# Always display the "Calculation Result"
if total_bill_converted is not None and price_per_person_converted is not None:
    st.subheader("Calculation Result")
    st.write(f"Tax: {tax:.2f} EUR")
    st.write(f"Tip: {tip:.2f} EUR")
    st.write(f"Total Bill: {total_bill_converted:.2f} {to_currency}")
    st.write(f"Price per Person: {price_per_person_converted:.2f} {to_currency}")

# ส่วนสำหรับการชำระเงิน
st.subheader("Payment")

# ดึง denominations จากสกุลเงินที่เลือก
selected_denominations = denominations[to_currency]

paid_amount = 0
payment_details = {}

for denomination in selected_denominations:
    count = st.number_input(f"{denomination}:", min_value=0, step=1, key=denomination)
    payment_details[denomination] = count
    paid_amount += count * selected_denominations[denomination]

# Pay button logic
if st.button("Pay"):
    if paid_amount >= total_bill_converted:
        change = paid_amount - total_bill_converted
        
        # แสดงใบเสร็จ
        display_receipt(bill_amount, tax, tip, total_bill_converted, price_per_person_converted, paid_amount, change, to_currency)

        bill_data = {
            'bill_amount': bill_amount,
            'change': change,
            'currency': to_currency,
            'paid_amount': paid_amount,
            'price_per_person': price_per_person_converted,
            'tax': tax,
            'timestamp': datetime.now(),
            'tip': tip,
            'total_bill': bill_amount
        }
        # ปุ่มพิมพ์ใบเสร็จ
        receipt = f"""
        Bill Amount: €{bill_amount:.2f}
        Tax: {tax:.2f} EUR
        Tip: {tip:.2f} EUR
        Total Bill: {total_bill_converted:.2f} {to_currency}
        Price per Person: {price_per_person_converted:.2f} {to_currency}
        Paid Amount: {paid_amount:.2f} {to_currency}
        Change: {change:.2f} {to_currency}
        """
        st.download_button("Download Receipt", receipt, file_name="receipt.txt")

        db.collection('Bill').add(bill_data)

        print("Document successfully written!")
    else:
        shortfall = total_bill_converted - paid_amount
        st.error(f"Not enough money provided. You need to add {shortfall:.2f} {to_currency}.")

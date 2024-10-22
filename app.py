import streamlit as st
import requests
from firebase_config import initialize_firebase
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
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        db.collection('receipts').add(receipt_data)
        st.success("บันทึกใบเสร็จสำเร็จในระบบคลาวด์")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึกใบเสร็จในระบบคลาวด์: {e}")

# ใส่ API Key ที่ได้รับ
api_key = '21766d7c69822a4e7d815c4f'

# รายการของธนบัตรตามสกุลเงิน
denominations = {
    "EUR": {
        "500 ยูโร": 500,
        "200 ยูโร": 200,
        "100 ยูโร": 100,
        "50 ยูโร": 50,
        "20 ยูโร": 20,
        "10 ยูโร": 10,
        "5 ยูโร": 5,
        "2 ยูโร": 2,
        "1 ยูโร": 1,
        "50 เซนต์": 0.50,
        "20 เซนต์": 0.20,
        "10 เซนต์": 0.10,
        "5 เซนต์": 0.05,
        "2 เซนต์": 0.02,
        "1 เซนต์": 0.01,
    },
    "THB": {
        "1000 บาท": 1000,
        "500 บาท": 500,
        "100 บาท": 100,
        "50 บาท": 50,
        "20 บาท": 20,
        "10 บาท": 10,
        "5 บาท": 5,
        "1 บาท": 1,
    },
    "USD": {
        "100 ดอลลาร์": 100,
        "50 ดอลลาร์": 50,
        "20 ดอลลาร์": 20,
        "10 ดอลลาร์": 10,
        "5 ดอลลาร์": 5,
        "1 ดอลลาร์": 1,
    },
    "JPY": {
        "10000 เยน": 10000,
        "5000 เยน": 5000,
        "2000 เยน": 2000,
        "1000 เยน": 1000,
        "500 เยน": 500,
        "100 เยน": 100,
        "50 เยน": 50,
        "10 เยน": 10,
        "5 เยน": 5,
        "1 เยน": 1,
    },
    "GBP": {
        "50 ปอนด์": 50,
        "20 ปอนด์": 20,
        "10 ปอนด์": 10,
        "5 ปอนด์": 5,
        "1 ปอนด์": 1,
    },
    "CNY": {
        "100 หยวน": 100,
        "50 หยวน": 50,
        "20 หยวน": 20,
        "10 หยวน": 10,
        "5 หยวน": 5,
        "1 หยวน": 1,
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
            st.error(f"เกิดข้อผิดพลาด: {data['error-type']}")
            return None
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
        return None

# ฟังก์ชันแสดงใบเสร็จ
def display_receipt(bill_amount, tax_converted, tip_converted, total_bill_converted, price_per_person_converted, paid_amount, change, currency):
    try:
        receipt = f"""
        <div style="border: 1px solid #ccc; border-radius: 10px; padding: 20px; width: 400px; margin: auto; font-family: Arial, sans-serif;">
            <h2 style="text-align: center; color: #007BFF;">ใบเสร็จ</h2>
            <p><strong>จำนวนเงินบิล:</strong> €{bill_amount:.2f}</p>
            <p><strong>ภาษี:</strong> {tax_converted:.2f} {currency}</p>
            <p><strong>ทิป:</strong> {tip_converted:.2f} {currency}</p>
            <p><strong>ยอดรวม:</strong> {total_bill_converted:.2f} {currency}</p>
            <p><strong>ราคาต่อคน:</strong> {price_per_person_converted:.2f} {currency}</p>
            <p><strong>จำนวนเงินที่ชำระ:</strong> {paid_amount:.2f} {currency}</p>
            <p><strong>เงินทอน:</strong> {change:.2f} {currency}</p>
            <p style="text-align: center; color: #28a745;">ขอบคุณที่ชำระเงิน!</p>
        </div>
        """
        st.markdown(receipt, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการแสดงใบเสร็จ: {e}")

# ส่วนอินเตอร์เฟสสำหรับการคำนวณบิล
st.title("เครื่องคำนวณบิล")
st.sidebar.header("กรอกข้อมูลบิล")

# อินพุตข้อมูลบิล
bill_amount = st.sidebar.number_input("จำนวนเงินบิล (EUR):", min_value=0.0, format="%.2f")
tax_rate = st.sidebar.number_input("อัตราภาษี (%):", min_value=0.0, format="%.2f")
tip_percentage = st.sidebar.number_input("เปอร์เซ็นต์ทิป (%):", min_value=0.0, format="%.2f")
num_people = st.sidebar.number_input("จำนวนคน:", min_value=1)

# ตัวเลือกสกุลเงินสำหรับการจ่าย
to_currency = st.sidebar.selectbox("เลือกสกุลเงินสำหรับการชำระ:", ["USD", "THB", "JPY", "GBP", "CNY", "EUR"])
tax, tip, total_bill, price_per_person = calculate_bill(bill_amount, tax_rate, tip_percentage, num_people)

# แปลงยอดรวม, ภาษี และทิปไปยังสกุลเงินที่เลือก
tax_converted = convert_currency(api_key, "EUR", to_currency, tax)
tip_converted = convert_currency(api_key, "EUR", to_currency, tip)
total_bill_converted = convert_currency(api_key, "EUR", to_currency, total_bill)
price_per_person_converted = convert_currency(api_key, "EUR", to_currency, price_per_person)

# แสดงผลลัพธ์การคำนวณ
if total_bill_converted is not None and price_per_person_converted is not None:
    st.subheader("ผลลัพธ์การคำนวณ")
    st.write(f"ภาษี: {tax_converted:.2f} {to_currency}")
    st.write(f"ทิป: {tip_converted:.2f} {to_currency}")
    st.write(f"ยอดรวม: {total_bill_converted:.2f} {to_currency}")
    st.write(f"ราคาต่อคน: {price_per_person_converted:.2f} {to_currency}")

# ส่วนสำหรับการชำระเงิน
st.subheader("การชำระเงิน")

# ดึงธนบัตรจากสกุลเงินที่เลือก
selected_denominations = denominations[to_currency]

paid_amount = 0
payment_details = {}

for denomination in selected_denominations:
    count = st.number_input(f"{denomination}:", min_value=0, step=1)
    if count > 0:
        payment_details[denomination] = count
        paid_amount += selected_denominations[denomination] * count

if st.button("คำนวณเงินทอนและแสดงใบเสร็จ"):
    if paid_amount >= total_bill_converted:
        change = paid_amount - total_bill_converted
        display_receipt(bill_amount, tax_converted, tip_converted, total_bill_converted, price_per_person_converted, paid_amount, change, to_currency)
        save_receipt_to_firestore(bill_amount, tax_converted, tip_converted, total_bill_converted, price_per_person_converted, paid_amount, change, to_currency)
        
        receipt_text = f"ใบเสร็จ\n\nจำนวนเงินบิล: €{bill_amount:.2f}\nภาษี: {tax_converted:.2f} {to_currency}\nทิป: {tip_converted:.2f} {to_currency}\nยอดรวม: {total_bill_converted:.2f} {to_currency}\nราคาต่อคน: {price_per_person_converted:.2f} {to_currency}\nจำนวนเงินที่ชำระ: {paid_amount:.2f} {to_currency}\nเงินทอน: {change:.2f} {to_currency}"
        
        st.download_button(
            label="ดาวน์โหลดใบเสร็จ",
            data=receipt_text,
            file_name="receipt.txt",
            mime="text/plain",
        )
    else:
        st.error(f"จำนวนเงินที่ชำระ {paid_amount:.2f} {to_currency} ไม่เพียงพอ")

import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import ast

load_dotenv()

users_df = pd.read_csv("C:\\Users\\saanc\\Desktop\\capstone project\\users.csv")
orders_df = pd.read_csv('C:\\Users\\saanc\\Desktop\\capstone project\\orders.csv')
products_df = pd.read_csv('C:\\Users\\saanc\\Desktop\\capstone project\\products.csv')
reviews_df = pd.read_csv('C:\\Users\\saanc\\Desktop\\capstone project\\reviews.csv')
faqs_df = pd.read_csv('C:\\Users\\saanc\\Desktop\\capstone project\\faqs.csv')

orders_df['products_ordered'] = orders_df['products_ordered'].apply(ast.literal_eval)

genai.configure(api_key="AIzaSyCWvIrva_vNjYh51Rfo8mhGDnzj8MRTo7I")
model = genai.GenerativeModel("gemini-pro")

st.set_page_config(page_title="Customer Support")
st.image("C:\\Users\\saanc\\Desktop\\capstone project\\download.png", width=200)
st.header("Customer Service")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'memory' not in st.session_state:
    st.session_state['memory'] = {}
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

if 'chat' not in st.session_state:
    st.session_state['chat'] = model.start_chat(history=[])

def get_gemini_response(question):
    chat = st.session_state['chat']
    response = chat.send_message(question, stream=True)
    return response

def handle_faq_response(question):
    for _, row in faqs_df.iterrows():
        faq_id = row['faq_id']
        faq_question = row['question']
        faq_answer = row['answer']
        if faq_question.lower() in question.lower():
            return faq_answer
    return None

def handle_automated_response(question):
    faq_response = handle_faq_response(question)
    if faq_response:
        return faq_response

    if "order status" in question.lower():
        user_id = st.session_state['user_id']
        order_status = orders_df[orders_df['user_id'] == user_id]['order_status'].tolist()
        return f"Your order status is {', '.join(order_status)}."
    elif any(keyword in question.lower() for keyword in ["delivery time", "shipping", "when will my order arrive"]):
        return "Our standard delivery time is 3-5 business days. You will receive a tracking number once your order ships."
    elif any(keyword in question.lower() for keyword in ["return policy", "exchange", "refund"]):
        return "Our return policy allows for returns within 30 days of purchase. Please visit our website for more details."
    elif "product availability" in question.lower():
        return "You can check the availability of products on our website or contact our customer support for assistance."
    elif any(keyword in question.lower() for keyword in ["account login", "forgot password", "reset password"]):
        return "You can reset your password by visiting the login page and following the 'Forgot Password' link."
    elif any(keyword in question.lower() for keyword in ["pricing", "cost", "discount"]):
        return "For pricing information, please check our website or contact our sales team for assistance."
    elif any(keyword in question.lower() for keyword in ["contact information", "phone number", "email address"]):
        return "You can find our contact information on our website's 'Contact Us' page."
    elif any(keyword in question.lower() for keyword in ["product information", "specifications", "customer reviews"]):
        return "You can find detailed product information, specifications, and customer reviews on our product pages."
    elif any(keyword in question.lower() for keyword in ["fabric types", "type of fabric", "material"]):
        fabric_type = question.lower().split()[-1]
        product_ids = products_df[products_df['fabric_type'].str.lower() == fabric_type]['product_id'].tolist()
        if product_ids:
            return f"Products made of {fabric_type} include: {', '.join(product_ids)}"
        else:
            return f"No products found with fabric type: {fabric_type}"
    elif any(keyword in question.lower() for keyword in ["fabric quality", "quality of fabric", "durability"]):
        fabric_type = get_user_preferences(st.session_state['user_id'])
        return f"Your preferred fabric is {fabric_type}, known for its quality and comfort."
    elif any(keyword in question.lower() for keyword in ["types of items", "product categories", "range of products"]):
        categories = products_df['category'].unique().tolist()
        return f"We offer a variety of categories including {', '.join(categories)}"
    elif any(keyword in question.lower() for keyword in ["sizes available", "available sizes"]):
        return "We offer sizes from XS to XL in most of our products."
    elif "return item" in question.lower():
        return "You can initiate a return through our website or contact customer support for assistance."
    elif "gift cards" in question.lower():
        return "Yes, we offer gift cards for purchase. They are available in various denominations."
    elif "shipping policy" in question.lower():
        return "We offer standard shipping within 3-5 business days. Expedited shipping options are also available."
    elif "contact support" in question.lower():
        return "You can contact our customer support team via email at support@example.com or by phone at +1234567890."
    elif "payment methods" in question.lower():
        return "We accept Visa, MasterCard, American Express, PayPal, and Apple Pay."
    elif "track order" in question.lower():
        return "Yes, you can track your order using the tracking link provided in your shipment confirmation email."
    elif "international shipping" in question.lower():
        return "Yes, we ship to several countries outside of the US. Shipping fees and delivery times may vary."
    elif "cancel order" in question.lower():
        return "To cancel an order, please contact customer support as soon as possible. Orders can only be canceled before they are shipped."
    elif any(keyword in question.lower() for keyword in ["fabrics used", "types of fabrics", "material"]):
        return "We use a variety of fabrics, including cotton, polyester, and blends. Specific fabric information is available on the product pages."
    elif "size guide" in question.lower():
        return "Yes, we provide a size guide on our website to help you choose the right fit."
    elif "create account" in question.lower():
        return "You can create an account by clicking the 'Sign Up' button on our website and following the instructions."
    elif "defective item" in question.lower():
        return "If you receive a defective item, please contact customer support immediately for assistance with a replacement or refund."
    elif "physical stores" in question.lower():
        return "Currently, we operate exclusively online and do not have physical store locations."
    elif "update account information" in question.lower():
        return "You can update your account information by logging into your account and navigating to the 'Account Settings' section."
    elif "change shipping address" in question.lower():
        return "If your order has not been shipped yet, you can update your shipping address by contacting customer support."
    elif "use promo code" in question.lower():
        return "You can apply a promo code at checkout in the designated field to receive a discount on your purchase."
    elif "membership benefits" in question.lower():
        return "Yes, members receive exclusive discounts, early access to sales, and other special offers."
    elif "exchange policy" in question.lower():
        return "We currently do not offer direct exchanges. Instead, please return the unwanted item and place a new order for the desired item."
    elif "loyalty program" in question.lower():
        return "Yes, we offer a loyalty program where you can earn points on purchases and redeem them for discounts and other perks."
    elif "unsubscribe newsletter" in question.lower():
        return "You can unsubscribe by clicking the 'Unsubscribe' link at the bottom of any newsletter email or by updating your preferences in your account settings."
    elif "contact page" in question.lower():
        return "For extra help, please visit our customer service contact page at [H&M Customer Service](https://www2.hm.com/en_in/customer-service/contact.html)."
    else:
        return None

def suggest_follow_up_questions(current_query, previous_queries):
    suggested_questions = []

    if "order status" in current_query.lower():
        suggested_questions.append("Can I track my order?")
        suggested_questions.append("What is the delivery time for my order?")
    elif "delivery time" in current_query.lower():
        suggested_questions.append("How can I expedite my shipping?")
        suggested_questions.append("Can I track my order?")
    elif "return policy" in current_query.lower():
        suggested_questions.append("How do I initiate a return?")
        suggested_questions.append("What is your exchange policy?")
    elif "product availability" in current_query.lower():
        suggested_questions.append("Can you notify me when this product is back in stock?")
        suggested_questions.append("Do you have this product in a different size?")
    elif "account login" in current_query.lower():
        suggested_questions.append("I forgot my password. How can I reset it?")
        suggested_questions.append("How do I update my account information?")
    elif "pricing" in current_query.lower():
        suggested_questions.append("Do you have any ongoing discounts or promotions?")
        suggested_questions.append("How can I apply a promo code to my order?")
    elif "contact information" in current_query.lower():
        suggested_questions.append("What are your customer service hours?")
        suggested_questions.append("Can I reach customer support via social media?")
    elif "product information" in current_query.lower():
        suggested_questions.append("Are there any customer reviews for this product?")
        suggested_questions.append("What are the specifications for this product?")
    elif "fabric types" in current_query.lower():
        suggested_questions.append("What fabric types are available for your products?")
        suggested_questions.append("Can you provide more details about the fabric quality?")
    elif "fabric quality" in current_query.lower():
        suggested_questions.append("Are there any specific care instructions for this fabric?")
        suggested_questions.append("What is the durability of this fabric like?")
    elif "types of items" in current_query.lower():
        suggested_questions.append("What are your best-selling items?")
        suggested_questions.append("Do you have any new arrivals?")
    elif "sizes available" in current_query.lower():
        suggested_questions.append("What size would you recommend for my measurements?")
        suggested_questions.append("Do you have a size guide?")
    elif "return item" in current_query.lower():
        suggested_questions.append("What is your return policy?")
        suggested_questions.append("How long does it take to process a return?")
    elif "gift cards" in current_query.lower():
        suggested_questions.append("How can I purchase a gift card?")
        suggested_questions.append("Are there any restrictions on using gift cards?")
    elif "shipping policy" in current_query.lower():
        suggested_questions.append("Do you offer expedited shipping options?")
        suggested_questions.append("Can I track my shipment?")
    elif "contact support" in current_query.lower():
        suggested_questions.append("What are your customer support hours?")
        suggested_questions.append("Can I reach customer support via social media?")
    elif "payment methods" in current_query.lower():
        suggested_questions.append("Do you accept international payment methods?")
        suggested_questions.append("Is it safe to use my credit card on your website?")
    elif "track order" in current_query.lower():
        suggested_questions.append("Can I track my order?")
        suggested_questions.append("What is the delivery time for my order?")
    elif "international shipping" in current_query.lower():
        suggested_questions.append("Do you offer expedited shipping options?")
        suggested_questions.append("Can I track my shipment?")
    elif "cancel order" in current_query.lower():
        suggested_questions.append("How can I cancel my order?")
        suggested_questions.append("What is your order cancellation policy?")
    elif "fabrics used" in current_query.lower():
        suggested_questions.append("What fabric types are available for your products?")
        suggested_questions.append("Can you provide more details about the fabric quality?")
    elif "size guide" in current_query.lower():
        suggested_questions.append("What size would you recommend for my measurements?")
        suggested_questions.append("Do you have a size guide?")
    elif "create account" in current_query.lower():
        suggested_questions.append("What are the benefits of creating an account?")
        suggested_questions.append("How do I update my account information?")
    elif "defective item" in current_query.lower():
        suggested_questions.append("How do I return a defective item?")
        suggested_questions.append("What is your return policy for defective items?")
    elif "physical stores" in current_query.lower():
        suggested_questions.append("Do you have any upcoming plans for physical stores?")
        suggested_questions.append("Can I return online purchases to a physical store?")
    elif "update account information" in current_query.lower():
        suggested_questions.append("How do I update my account information?")
        suggested_questions.append("Can I change my email address or phone number?")
    elif "change shipping address" in current_query.lower():
        suggested_questions.append("How do I change my shipping address?")
        suggested_questions.append("Can I update my shipping address after placing an order?")
    elif "use promo code" in current_query.lower():
        suggested_questions.append("How do I apply a promo code to my order?")
        suggested_questions.append("Do you have any ongoing discounts or promotions?")
    elif "membership benefits" in current_query.lower():
        suggested_questions.append("What are the benefits of becoming a member?")
        suggested_questions.append("How do I sign up for your membership program?")
    elif "exchange policy" in current_query.lower():
        suggested_questions.append("What is your exchange policy?")
        suggested_questions.append("How do I exchange an item?")
    elif "loyalty program" in current_query.lower():
        suggested_questions.append("How do I sign up for your loyalty program?")
        suggested_questions.append("What are the benefits of joining your loyalty program?")
    elif "unsubscribe newsletter" in current_query.lower():
        suggested_questions.append("How do I unsubscribe from your newsletter?")
        suggested_questions.append("Can I update my newsletter preferences?")
    elif "contact page" in current_query.lower():
        suggested_questions.append("What are your customer service hours?")
        suggested_questions.append("Can I reach customer support via social media?")
    else:
        suggested_questions.append("Can you help me with something else?")
    
    return suggested_questions

def log_in(email, phone_number):
    user = users_df[(users_df['email'] == email) & (users_df['phone_number'] == phone_number)]
    if not user.empty:
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = user['user_id'].values[0]
        return True
    else:
        return False

if not st.session_state['logged_in']:
    email = st.text_input("Email")
    phone_number = st.text_input("Phone Number")
    if st.button("Log In"):
        if log_in(email, phone_number):
            st.success("Logged in successfully!")
        else:
            st.error("Invalid email or phone number. Please try again.")
else:
    st.write("You are logged in.")
    question = st.text_input("How can I help you?")
    if st.button("Send"):
        response = handle_automated_response(question)
        if not response:
            response = get_gemini_response(question)
        st.session_state['chat_history'].append({"question": question, "response": response})
        st.write(response)
        suggested_questions = suggest_follow_up_questions(question, st.session_state['chat_history'])
        st.write("Suggested follow-up questions:")
        for sq in suggested_questions:
            st.write("- " + sq)

from flask_mail import Message
from db_ext import mail

def send_todo_email(to_email, title, description):
    from flask_mail import Message
    from db_ext import mail

    subject = "✅ New Todo Created!"
    html_content = f"""
    <html><body>
        <h2>📌 New Todo Added!</h2>
        <p><b>Title:</b> {title}</p>
        <p><b>Description:</b> {description}</p>
    </body></html>
    """

    msg = Message(
        subject,
        recipients=[to_email],
        sender="sawanrawat2004@gmail.com"  
    )
    msg.html = html_content

    try:
        mail.send(msg)
        print("✅ Email sent successfully.")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

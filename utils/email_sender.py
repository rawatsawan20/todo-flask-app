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
        sender="your_email@gmail.com"  # Must match MAIL_DEFAULT_SENDER in config
    )
    msg.html = html_content

    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

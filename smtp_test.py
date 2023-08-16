import smtplib
import os
try:
    email_user = os.environ.get('EMAIL_HOST_USER')
    email_pass = os.environ.get('EMAIL_HOST_PASSWORD')
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print(f"Email User: {email_user}")
    print(f"Email Password: {email_pass}")
    server.login(email_user,email_pass)
    server.sendmail('sagnik.chakraborty@tib.edu.in', 'receiver_email@gmail.com', 'Test mail sucessssss.')
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")

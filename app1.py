import tkinter as tk
from tkinter import messagebox
from flask import Flask, request
from flask_mail import Mail, Message
import imaplib
import email
from email.header import decode_header

# 创建 Flask 应用
app = Flask(__name__)

# 邮件配置（请替换为你的邮箱和授权码）
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '你的邮箱@qq.com'  # 填写你的 QQ 邮箱
app.config['MAIL_PASSWORD'] = '你的授权码'  # 填写你的 QQ 授权码

mail = Mail(app)

# Tkinter GUI 应用
class EmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QQ Email Reader and Sender")

        # 输入框
        tk.Label(root, text="QQ Email:").grid(row=0, column=0)
        self.username_entry = tk.Entry(root)
        self.username_entry.grid(row=0, column=1)

        tk.Label(root, text="Authorization Code:").grid(row=1, column=0)
        self.password_entry = tk.Entry(root, show='*')
        self.password_entry.grid(row=1, column=1)

        # 按钮
        tk.Button(root, text="Read Latest Email", command=self.read_email).grid(row=2, columnspan=2)

        # 邮件发送部分
        tk.Label(root, text="Recipient:").grid(row=3, column=0)
        self.recipient_entry = tk.Entry(root)
        self.recipient_entry.grid(row=3, column=1)

        tk.Label(root, text="Subject:").grid(row=4, column=0)
        self.subject_entry = tk.Entry(root)
        self.subject_entry.grid(row=4, column=1)

        tk.Label(root, text="Email Body:").grid(row=5, column=0)
        self.body_entry = tk.Text(root, height=5, width=30)
        self.body_entry.grid(row=5, column=1)

        tk.Button(root, text="Send Email", command=self.send_email).grid(row=6, columnspan=2)

    def read_email(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            mail_server = imaplib.IMAP4_SSL('imap.qq.com')
            mail_server.login(username, password)
            mail_server.select('inbox')

            status, messages = mail_server.search(None, 'ALL')
            mail_ids = messages[0].split()
            if not mail_ids:
                messagebox.showerror("Error", "No emails found.")
                return

            latest_email_id = mail_ids[-1]
            status, msg_data = mail_server.fetch(latest_email_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            # 解码主题
            subject, encoding = decode_header(msg['subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else 'utf-8')

            # 解码发件人
            from_ = msg['from']
            from_header = decode_header(from_)[0]
            if isinstance(from_header[0], bytes):
                from_ = from_header[0].decode(from_header[1] if from_header[1] else 'utf-8')

            # 邮件内容
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                        break
            else:
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')

            mail_server.logout()

            messagebox.showinfo("Email Content", f"Subject: {subject}\nFrom: {from_}\nBody: {body}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def send_email(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        to = self.recipient_entry.get()
        subject = self.subject_entry.get()
        body = self.body_entry.get("1.0", tk.END).strip()  # 获取文本框内容

        # 确保所有内容使用 UTF-8 编码
        try:
            msg = Message(subject=subject, sender=username, recipients=[to])
            msg.body = body.encode('utf-8')  # 确保使用 UTF-8 编码

            mail.send(msg)
            messagebox.showinfo("Success", "Email sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == '__main__':
    root = tk.Tk()
    app = EmailApp(root)
    root.mainloop()

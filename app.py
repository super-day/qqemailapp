from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
import imaplib
import email
from email.header import decode_header

app = Flask(__name__)

# 配置邮件服务器
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587  # 使用 TLS
app.config['MAIL_USE_TLS'] = True  # 启用 TLS
app.config['MAIL_USE_SSL'] = False  # 禁用 SSL
app.config['MAIL_USERNAME'] = '3629029135@qq.com'  # 填写你的 QQ 邮箱
app.config['MAIL_PASSWORD'] = 'lwklnpmrpjzcchhb'  # 填写你的 QQ 邮箱授权码

# 初始化 Flask-Mail
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/read_email', methods=['POST'])
def read_email():
    username = request.json.get('username')
    password = request.json.get('password')

    mail_server = imaplib.IMAP4_SSL('imap.qq.com')
    try:
        mail_server.login(username, password)
    except imaplib.IMAP4.error:
        return jsonify({'error': 'Login failed. Check your email and authorization code.'}), 401

    mail_server.select('inbox')

    status, messages = mail_server.search(None, 'ALL')
    mail_ids = messages[0].split()
    if not mail_ids:
        return jsonify({'error': 'No emails found.'}), 404

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
    else:
        from_ = from_header[0]  # 如果不是字节，直接赋值

    # 处理邮件内容
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                break
    else:
        body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')

    mail_server.logout()

    return jsonify({
        'subject': subject,
        'from': from_,
        'body': body
    })


@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.json

    # 验证输入字段
    try:
        username = str(data['username'])
        password = str(data['password'])
        subject = str(data.get('subject', 'No Subject'))
        recipient = str(data['to'])
        body = str(data.get('body', 'No Content'))
    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400  # 返回 400 错误

    # 创建邮件消息
    msg = Message(subject=subject, sender=username, recipients=[recipient])
    msg.body = body  # 设置邮件正文

    try:
        print(f'Sending email to: {recipient} with subject: "{subject}" and body: "{body}"')
        mail.send(msg)
    except Exception as e:
        error_message = str(e)
        print(f'Error occurred while sending email: {error_message}')  # 输出错误信息到控制台
        return jsonify({'error': f'Failed to send email: {error_message}'}), 500

    return jsonify({'status': 'Email sent!'}), 200

if __name__ == '__main__':
    app.run(debug=True)

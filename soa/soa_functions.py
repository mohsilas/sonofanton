import os
import time
import email
import imaplib
from pathlib import Path
from datetime import datetime
import anthropic
import subprocess
import http.client
import urllib
import markdown
import json
from typing import Dict, Optional, Union

class SOAService:
    def __init__(self, email_address: str, password: str, admin_code, anthropic_key: str,
                 pushover_token: str, pushover_user: str, imap_server: str = "imap.gmail.com"):
        self.email_address = email_address
        self.admin_code = admin_code # mine is 'SUBJECT "AdminCode-xxxxx-xxx-xxx-xxx"', that way only emails with this specific subject get picked up by anton
        self.password = password
        self.imap_server = imap_server
        self.client = anthropic.Anthropic(api_key=anthropic_key)
        self.pushover_token = pushover_token
        self.pushover_user = pushover_user

    def toolset_load(self):
        with open('tools.json') as f:
            jsn = json.load(f)
        return jsn

    def mail_check(self) -> list:
        imap = None
        try:
            imap = imaplib.IMAP4_SSL(self.imap_server)
            imap.login(self.email_address, self.password)
            imap.select("INBOX")

            _, message_numbers = imap.search(None, f'(UNSEEN {self.admin_code})')

            if not message_numbers[0]:
                return [None, None]

            latest = message_numbers[0].split()[-1]
            _, msg_data = imap.fetch(latest, '(RFC822)')
            email_msg = email.message_from_bytes(msg_data[0][1])

            content = ""
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            content = payload.decode()
                            break
            else:
                content = email_msg.get_payload(decode=True).decode()

            imap.store(latest, "+FLAGS", "\\Seen")

            return [email_msg["from"], content]

        except imaplib.IMAP4.error as e:
            #print(f"IMAP error: {str(e)}")
            return [None, None]
        except Exception as e:
            #print(f"Error checking mail: {str(e)}")
            return [None, None]
        finally:
            if imap:
                try:
                    imap.logout()
                except:
                    pass

    def claude(self, prompt: str) -> str:
        message = self.client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return str(message.content[0].text).strip()

    def claude_fast(self, prompt: str) -> str:
        message = self.client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return str(message.content[0].text).strip()

    def tool_use(self, prompt: str) -> str:
        message = self.client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=1024,
            tools = self.toolset_load(),
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[1]

    def notification_send(self, message: str, title: Optional[str] = None, priority: int = 0,
                         url: Optional[str] = None, file_path: Optional[str] = None) -> Dict:
        try:
            import os
            from urllib.parse import urlencode
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email.mime.application import MIMEApplication

            payload = {
                "token": self.pushover_token,
                "user": self.pushover_user,
                "message": message,
                "priority": priority
            }
            if title:
                payload["title"] = title
            if url:
                payload["url"] = url

            conn = http.client.HTTPSConnection("api.pushover.net:443")

            if file_path:
                boundary = 'PushoverBoundary'
                body = []

                # Add regular form fields
                for key, value in payload.items():
                    body.append(f'--{boundary}'.encode('utf-8'))
                    body.append(f'Content-Disposition: form-data; name="{key}"'.encode('utf-8'))
                    body.append(b'')
                    body.append(str(value).encode('utf-8'))

                # Add file
                filename = os.path.basename(file_path)
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    body.append(f'--{boundary}'.encode('utf-8'))
                    body.append(f'Content-Disposition: form-data; name="attachment"; filename="{filename}"'.encode('utf-8'))
                    body.append(b'Content-Type: application/octet-stream')
                    body.append(b'')
                    body.append(file_data)

                body.append(f'--{boundary}--'.encode('utf-8'))
                body = b'\r\n'.join(body)

                headers = {
                    'Content-Type': f'multipart/form-data; boundary={boundary}',
                    'Content-Length': str(len(body))
                }

                conn.request('POST', '/1/messages.json', body, headers)
            else:
                conn.request(
                    "POST",
                    "/1/messages.json",
                    urlencode(payload),
                    {"Content-type": "application/x-www-form-urlencoded"}
                )

            response = conn.getresponse()
            return json.loads(response.read().decode())
        finally:
            conn.close()

    def save_file(self, content, path):
        existed = os.path.exists(path)
        name = os.path.basename(path)
        with open(path, 'w') as f:
            f.write(content)
        return f"file: {name} was updated" if existed else f"file: {name} was saved"


    def run_script(self, script_path, args=None):
        try:
            cmd = ['python', script_path] + (args or [])
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Failed with error: {result.stderr}"
        except Exception as e:
            return f"Failed to execute: {str(e)}"

    def run_tool(self, tool):
        fn_name = tool.name
        fn_input = tool.input

        func = getattr(self, fn_name)
        try:
            kwargs = {k: v for k, v in fn_input.items()}
            return func(**kwargs)
        except Exception as e:
            return f"tool use error: {e}"


    def update_blog(self, content):
        try:
            html_content = markdown.markdown(content)
            current_year = datetime.now().year

            template = '''
            <!DOCTYPE html>
                <html lang="en" class="light">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Inside The Machines</title>
                    <link href="https://fonts.googleapis.com/css2?family=Domine:wght@400..700&family=Lora:ital,wght@0,400..700;1,400..700&family=Roboto+Serif:ital,opsz,wght@0,8..144,100..900;1,8..144,100..900&display=swap" rel="stylesheet">
                    <style>
                        :root {{
                            --bg-color: #ffffff;
                            --text-color: #1a1a1a;
                            --accent-color: #0066cc;
                            --heading-font: 'Roboto Serif', serif;
                            --body-font: 'Lora', serif;
                        }}

                        .dark {{
                            --bg-color: #1a1a1a;
                            --text-color: #ffffff;
                            --accent-color: #66b3ff;
                        }}

                        body {{
                            font-family: var(--body-font);
                            line-height: 1.6;
                            max-width: min(800px, 90vw);
                            margin: 0 auto;
                            padding: 1rem;
                            background: var(--bg-color);
                            color: var(--text-color);
                            transition: background-color 0.3s, color 0.3s;
                            min-height: 100vh;
                            display: flex;
                            flex-direction: column;
                        }}

                        header {{
                            text-align: center;
                            margin-bottom: 2rem;
                            font-family: var(--heading-font);
                        }}

                        header h1 {{
                            font-size: clamp(1.5rem, 5vw, 2.5rem);
                            margin: 0;
                            font-weight: 700;
                        }}

                        h1, h2, h3 {{
                            color: var(--accent-color);
                            font-family: var(--heading-font);
                        }}

                        a {{
                            color: var(--accent-color);
                            text-decoration: none;
                        }}

                        img {{
                            max-width: 100%;
                            height: auto;
                        }}

                        pre, code {{
                            background: #2d2d2d;
                            color: #ccc;
                            padding: 0.2em 0.4em;
                            border-radius: 3px;
                            font-size: 0.9em;
                            overflow-x: auto;
                        }}

                        .theme-toggle {{
                            position: fixed;
                            top: 1rem;
                            right: 1rem;
                            padding: 0.5rem;
                            background: transparent;
                            border: none;
                            font-size: 1.5rem;
                            cursor: pointer;
                            z-index: 1000;
                        }}

                        article {{
                            flex: 1;
                        }}

                        footer {{
                            margin-top: 4rem;
                            padding: 2rem 0;
                            text-align: center;
                            font-size: 0.9rem;
                            opacity: 0.8;
                            border-top: 1px solid var(--text-color);
                        }}

                        @media (max-width: 768px) {{
                            body {{
                                padding: 0.5rem;
                            }}

                            .theme-toggle {{
                                top: 0.5rem;
                                right: 0.5rem;
                            }}
                        }}
                    </style>
                </head>
                <body>
                    <button class="theme-toggle" onclick="toggleTheme()">☀️</button>
                    <header>
                        <h1>👾 Inside The Machines 👾</h1>
                    </header>
                    <article>
                        {content}
                    </article>
                    <footer>
                        <p>© {year} Inside The Machines. <a href="mailto:mohsilas@outlook.com">contact writer ✉️</a></p>
                    </footer>

                    <script>
                        const themeToggle = document.querySelector('.theme-toggle');
                        function toggleTheme() {{
                            document.documentElement.classList.toggle('dark');
                            themeToggle.textContent = document.documentElement.classList.contains('dark') ? '🌙' : '☀️';
                        }}
                    </script>
                </body>
                </html>
            '''

            html_output = template.format(content=html_content, year=current_year)
            output_file = Path('index.html')  # Always write to index.html

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_output)

            cmd = ['python3', 'blog_git_commit.py'] # needs gh cli to be set up
            result = subprocess.run(cmd, capture_output=True, text=True)

            return f"blog post published: {result}"
        except Exception as e:
            return f"blog update failed. Error: {e}"

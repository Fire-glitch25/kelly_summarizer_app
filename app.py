import streamlit as st
from transformers import pipeline
from fpdf import FPDF

app = Flask(__name__)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Kelly Summarizer</title>
    <style>
        body {{
            background-image: url('https://images.unsplash.com/photo-1607746882042-944635dfe10e?auto=format&fit=crop&w=1470&q=80');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            text-align: center;
        }}
        h1 {{
            margin-top: 40px;
            font-size: 3em;
        }}
        form {{
            margin-top: 30px;
        }}
        textarea {{
            width: 80%;
            height: 200px;
            padding: 10px;
            font-size: 1.2em;
            border-radius: 10px;
            border: none;
            resize: none;
        }}
        .btn {{
            margin-top: 20px;
            padding: 12px 24px;
            font-size: 1em;
            border-radius: 8px;
            border: none;
            background-color: #ff4e84;
            color: white;
            cursor: pointer;
        }}
        .result {{
            background-color: rgba(0, 0, 0, 0.6);
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
            display: inline-block;
        }}
        #snow {{
            position: fixed;
            width: 100%;
            height: 100%;
            z-index: -1;
            top: 0;
            left: 0;
        }}
    </style>
</head>
<body>
    <canvas id="snow"></canvas>
    <h1>📝 Kelly Summarizer</h1>
    <form method="post">
        <textarea name="text" placeholder="Paste text here..." required>{text}</textarea><br>
        <button class="btn" type="submit">Summarize</button>
        {download_button}
    </form>
    {summary_section}
    <script>
        // ❄️ Snowfall Animation
        const canvas = document.getElementById('snow');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        let particles = [];

        for (let i = 0; i < 200; i++) {{
            particles.push({{
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                r: Math.random() * 4 + 1,
                d: Math.random() * 100
            }});
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "white";
            ctx.beginPath();
            for (let i = 0; i < particles.length; i++) {{
                let p = particles[i];
                ctx.moveTo(p.x, p.y);
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2, true);
            }}
            ctx.fill();
            update();
        }}

        let angle = 0;
        function update() {{
            angle += 0.01;
            for (let i = 0; i < particles.length; i++) {{
                let p = particles[i];
                p.y += Math.cos(angle + p.d) + 1 + p.r / 2;
                p.x += Math.sin(angle) * 2;

                if (p.x > canvas.width + 5 || p.x < -5 || p.y > canvas.height) {{
                    if (i % 3 > 0) {{
                        particles[i] = {{ x: Math.random() * canvas.width, y: -10, r: p.r, d: p.d }};
                    }} else {{
                        if (Math.sin(angle) > 0) {{
                            particles[i] = {{ x: -5, y: Math.random() * canvas.height, r: p.r, d: p.d }};
                        }} else {{
                            particles[i] = {{ x: canvas.width + 5, y: Math.random() * canvas.height, r: p.r, d: p.d }};
                        }}
                    }}
                }}
            }}
        }}
        setInterval(draw, 33);
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def summarize():
    summary = ''
    download_button = ''
    text = ''
    summary_section = ''
    if request.method == 'POST':
        text = request.form['text']
        if text:
            summary = summarizer(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
            download_button = '<br><a href="/download?summary=' + summary.replace(" ", "%20") + '" class="btn">📥 Download PDF</a>'
            summary_section = f'<div class="result"><h3>Summary:</h3><p>{summary}</p></div>'
    return HTML_TEMPLATE.format(summary=summary, download_button=download_button, summary_section=summary_section, text=text)

@app.route('/download')
def download():
    summary = request.args.get('summary', '')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary)
    response = Response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Disposition'] = 'attachment; filename=summary.pdf'
    response.mimetype = 'application/pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)

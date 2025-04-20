from flask import Flask, request, redirect, url_for, send_file, session, render_template_string
from openai import OpenAI
from xhtml2pdf import pisa
from io import BytesIO

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Groq AI API
api_key = "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"
client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

# HTML Template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>AI Study Plan Generator</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
  <style>
    body {
      background-image: url('https://uploads-ssl.webflow.com/60babc2f4a97cece9858d8e7/634f6224f7785fef6fb21cd3_hq720.jpeg');
      background-size: cover;
      background-position: center;
      background-attachment: fixed;
    }
    @keyframes fadeInUp {
      0% { opacity: 0; transform: translateY(30px); }
      100% { opacity: 1; transform: translateY(0); }
    }
    .fade-in { animation: fadeInUp 0.8s ease-out; }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center p-6">
  <div class="max-w-4xl w-full bg-white bg-opacity-60 backdrop-blur-lg border border-white border-opacity-30 p-10 rounded-2xl shadow-2xl fade-in">
    {% if plan %}
    <div class="prose max-w-full text-gray-900">
      <h2 class="text-2xl font-bold mb-4">Your Study Plan</h2>
      <pre class="whitespace-pre-wrap bg-white p-4 rounded-md">{{ plan }}</pre>
      <a href="{{ url_for('download_pdf') }}" class="mt-4 inline-block bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700">Download as PDF</a>
      <a href="{{ url_for('index') }}" class="mt-2 inline-block ml-4 text-indigo-700 underline">Generate Another Plan</a>
    </div>
    {% else %}
    <!-- Header -->
    <div class="text-center mb-8">
      <div class="flex justify-center mb-4">
        <img src="https://cdn-icons-png.flaticon.com/512/3658/3658753.png" alt="AI Icon" class="w-16 h-16">
      </div>
      <h1 class="text-4xl font-extrabold text-indigo-800">AI Study Planner</h1>
      <p class="mt-2 text-gray-700">Plan smarter, study better — powered by AI.</p>
    </div>

    <!-- Form -->
    <form method="post" action="/" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Subject</label>
        <input type="text" name="subject" required class="p-3 border border-gray-300 w-full rounded-lg focus:ring-2 focus:ring-indigo-400" placeholder="e.g., Math, Science">
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Study Hours per Day</label>
        <input type="number" name="time" required class="p-3 border border-gray-300 w-full rounded-lg focus:ring-2 focus:ring-indigo-400" placeholder="e.g., 4">
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Number of Days</label>
        <input type="number" name="days" required class="p-3 border border-gray-300 w-full rounded-lg focus:ring-2 focus:ring-indigo-400" placeholder="e.g., 30">
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Syllabus / Topics</label>
        <textarea name="syllabus" required class="p-3 border border-gray-300 w-full rounded-lg h-28 resize-none focus:ring-2 focus:ring-indigo-400" placeholder="Enter syllabus or specific topics"></textarea>
      </div>
      <div class="md:col-span-2">
        <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition flex items-center justify-center space-x-2">
          <span>🎯</span>
          <span>Generate Study Plan</span>
        </button>
      </div>
    </form>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        subject = request.form['subject']
        time = request.form['time']
        days = request.form['days']
        syllabus = request.form['syllabus']

        prompt = (
            f"Generate a human-readable and well-structured {days}-day study plan "
            f"for the subject: {subject}. Assume {time} hours of study per day. "
            f"Make sure to distribute the following syllabus/topics across the days: {syllabus}. "
            f"Format the response with clear Day headings and bullet points for topics/tasks."
        )

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )

        plan = response.choices[0].message.content
        session['generated_plan'] = plan
        return render_template_string(html_template, plan=plan)
    return render_template_string(html_template, plan=None)

@app.route('/download')
def download_pdf():
    plan = session.get('generated_plan', None)
    if not plan:
        return redirect(url_for('index'))

    pdf_buffer = BytesIO()
    html = f"<h1>Study Plan</h1><pre>{plan}</pre>"
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        return "Error creating PDF", 500

    pdf_buffer.seek(0)
    return send_file(pdf_buffer, download_name="study_plan.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

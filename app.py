import html 
import requests 
import streamlit as st 

APP_NAME = "Medical-Assitant"
API_URL = "http://127.0.0.1:8000/question"
REQUEST_TIMEOUT = 180 

EXAMPLES = [
    "What is the function of the nephron in the kidney?",
    "What are the main functions of the skeletal system?",
    "What is pneumonia and what are its common symptoms?",
]

st.set_page_config(
    page_title=f"{APP_NAME} - medical question, answered and illustrated",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS style 
CSS =  """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Literata:ital,opsz,wght@0,7..72,400..700;1,7..72,400..600&display=swap');
 
:root {
  --cream: #FAF8D4;
  --sand: #EBDCCB;
  --taupe: #C3BAAA;
  --mauve: #91818A;
  --ink: #3D3339;
  --ink-soft: #5E5058;
  --ui: 'Bricolage Grotesque', 'Segoe UI', system-ui, sans-serif;
  --read: 'Literata', Georgia, 'Times New Roman', serif;
}
 
/* ---------- page ---------- */
.stApp { background: var(--cream); color: var(--ink); }
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stMainBlockContainer"], .block-container {
  max-width: 1060px;
  padding-top: 2rem;
  padding-bottom: 4rem;
}
 
/* ---------- text ---------- */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
  font-family: var(--read);
  color: var(--ink);
  font-size: 1.05rem;
  line-height: 1.75;
}
.section-title {
  font-family: var(--ui) !important;
  font-weight: 700;
  font-size: 1.6rem;
  line-height: 1.2;
  color: var(--ink) !important;
  margin: 1.6rem 0 .7rem 0 !important;
  padding: 0 !important;
  letter-spacing: -0.01em;
}
.sub-title {
  font-family: var(--ui) !important;
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--ink) !important;
  margin: 0 0 .3rem 0 !important;
  padding: 0 !important;
}
.lead { font-size: 1.15rem !important; max-width: 68ch; }
.hint, .note {
  font-family: var(--read);
  font-size: .92rem !important;
  color: var(--ink-soft) !important;
  line-height: 1.6;
}
.asked { font-family: var(--ui); color: var(--ink-soft); margin: 0 0 .8rem 0; }
 
/* ---------- hero ---------- */
.hero {
  background: var(--sand);
  border-left: 8px solid var(--mauve);
  border-radius: 4px 22px 22px 4px;
  padding: 2.2rem 2.4rem 2.3rem 2.4rem;
  margin-bottom: 1.6rem;
}
.brand {
  font-family: var(--ui);
  font-weight: 600;
  font-size: 1.05rem;
  color: var(--ink-soft);
  margin-bottom: 1.1rem;
}
.brand-mark { color: var(--mauve); margin-right: .45rem; font-size: 1.2rem; }
.hero-title {
  font-family: var(--ui) !important;
  font-weight: 700;
  font-size: clamp(1.9rem, 4.2vw, 3rem);
  line-height: 1.08;
  letter-spacing: -0.02em;
  color: var(--ink) !important;
  max-width: 20ch;
  margin: 0 0 1rem 0 !important;
  padding: 0 !important;
}
.hero-text { max-width: 62ch; font-size: 1.1rem !important; color: var(--ink-soft) !important; margin: 0; }
 
/* ---------- tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 1.8rem; border-bottom: 2px solid var(--taupe); }
.stTabs [data-baseweb="tab"] { background: transparent; padding: .7rem .1rem; }
.stTabs [data-baseweb="tab"] p {
  font-family: var(--ui) !important;
  font-weight: 600;
  font-size: 1.1rem !important;
  color: var(--ink-soft) !important;
}
.stTabs [aria-selected="true"] p { color: var(--ink) !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--mauve) !important; height: 4px; }
.stTabs [data-baseweb="tab-border"] { background: transparent; }
 
/* ---------- question box ---------- */
[data-testid="stTextAreaRootElement"],
div[data-baseweb="textarea"] {
  background: var(--sand) !important;
  border: 2px solid var(--taupe) !important;
  border-radius: 12px !important;
}
[data-testid="stTextAreaRootElement"]:focus-within,
div[data-baseweb="textarea"]:focus-within {
  border-color: var(--mauve) !important;
  box-shadow: 0 0 0 4px rgba(145, 129, 138, .30) !important;
}
[data-testid="stTextArea"] textarea {
  background: transparent !important;
  color: var(--ink) !important;
  -webkit-text-fill-color: var(--ink) !important;
  caret-color: var(--ink);
  font-family: var(--read);
  font-size: 1.15rem;
  line-height: 1.6;
  padding: 1rem 1.1rem;
}
[data-testid="stTextArea"] textarea::placeholder { color: var(--ink-soft); opacity: .8; }
 
/* ---------- buttons ---------- */
.stButton > button {
  background: transparent;
  border: 1.5px solid var(--taupe);
  border-radius: 999px;
  padding: .4rem 1.1rem;
  transition: background .15s ease, border-color .15s ease;
}
.stButton > button p {
  font-family: var(--ui) !important;
  font-weight: 600;
  font-size: .98rem !important;
  color: var(--ink) !important;
  line-height: 1.4;
  margin: 0;
}
.stButton > button:hover { background: var(--sand); border-color: var(--mauve); }
.stButton > button:focus-visible { outline: 3px solid var(--mauve); outline-offset: 2px; }
.stButton > button[kind="primary"] {
  background: var(--ink-soft);
  border: none;
  border-radius: 10px;
  padding: .75rem 1.8rem;
}
.stButton > button[kind="primary"] p { color: var(--cream) !important; font-size: 1.1rem !important; }
.stButton > button[kind="primary"]:hover { background: var(--ink); }
 
/* ---------- alerts + expander ---------- */
[data-testid="stAlert"] {
  background: var(--sand);
  border: 1.5px solid var(--taupe);
  border-radius: 10px;
}
[data-testid="stAlert"] p { color: var(--ink) !important; }
[data-testid="stExpander"] details {
  background: var(--sand);
  border: 1.5px solid var(--taupe);
  border-radius: 10px;
}
[data-testid="stExpander"] summary p {
  font-family: var(--ui) !important;
  font-weight: 600;
  font-size: 1.05rem !important;
}
[data-testid="stSpinner"] p { font-family: var(--ui); color: var(--ink-soft); }
 
/* ---------- answer + figure ---------- */
.answer-card {
  background: var(--sand);
  border: 1.5px solid var(--taupe);
  border-radius: 8px;
  padding: 1.5rem 1.8rem;
}
.answer-card p:last-child { margin-bottom: 0; }
.plate {
  margin: 0;
  background: var(--sand);
  border: 2px solid var(--mauve);
  border-radius: 4px;
  padding: .7rem;
}
.plate img { display: block; width: 100%; height: auto; border-radius: 2px; }
.plate figcaption {
  font-family: var(--read);
  font-style: italic;
  font-size: .9rem;
  line-height: 1.55;
  color: var(--ink-soft);
  margin-top: .7rem;
}
.plate-missing {
  background: var(--sand);
  border: 2px dashed var(--taupe);
  border-radius: 4px;
  padding: 1.4rem;
  font-family: var(--read);
  color: var(--ink-soft);
  line-height: 1.6;
}
 
/* ---------- how it works ---------- */
.journey {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin: 1.2rem 0 .5rem 0;
}
.station {
  background: var(--sand);
  border: 1.5px solid var(--taupe);
  border-radius: 10px;
  padding: 1.1rem 1.2rem 1.2rem 1.2rem;
}
.station-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: var(--ink-soft);
  color: var(--cream);
  font-family: var(--ui);
  font-weight: 700;
  margin-bottom: .6rem;
}
.station p { margin: 0; font-size: 1rem !important; line-height: 1.6 !important; }
.station .sub-title { font-size: 1.1rem; }
 
.panel { border-radius: 14px; padding: 1.5rem 1.6rem 1.3rem 1.6rem; height: 100%; }
.panel-text { background: var(--sand); }
.panel-image { background: var(--taupe); }
.panel ol { margin: .8rem 0 0 0; padding-left: 1.3rem; }
.panel li { margin-bottom: .8rem; }
.panel li strong, .plain li strong { font-family: var(--ui); font-weight: 700; }
 
.plain { margin: .3rem 0 0 0; padding-left: 1.2rem; }
.plain li { margin-bottom: .7rem; }
 
@media (max-width: 640px) {
  .hero { padding: 1.5rem 1.3rem 1.6rem 1.3rem; }
  .answer-card { padding: 1.2rem; }
}
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def md(html_text: str):
    """Show HTML. leading spaces and blank lines are removed as Mardown never mistakes the HTML for code."""
    lines = [line.strip() for line in html_text.splitlines() if line.strip()]
    st.markdown("\n".join(lines), unsafe_allow_html=True)


def use_example(text: str):
    """Runs when a example button is clicked: puts the example in the question box."""
    st.session_state['question'] = text 


def ask_backend(question: str) -> dict:
    """Send the question to FastAPI, Returns {'answer':..., 'mage_base64':...}."""
    response = requests.post(API_URL, json={'question': question}, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json() 


def show_result(result: dict):
    """Show the written answer (left) and the illustration (right)."""
    question = html.escape(result['question'])
    col_answer, col_image = st.columns([3, 2], gap='large')

    with col_answer:
        md('<h3 class="sub-title">Answer</h3>')
        md(f'<p class="asked"> You asked: <em>{question}</em></p>')
        if result['answer']:
            st.markdown(f'<div class="answer-card">\n\n{result["answer"]}\n\n</div>', unsafe_allow_html=True)
        else:
            st.info("The back-end did not return an answer. Try asking again.")


    with col_image:
        md('<h3 class="sub-title">illustration</h3>')
        if result['image']:
            md(f""" 
                <figure class = 'plate'>
                <img src="data:image/png;base64,{result['image']}" alt="Illustration for: {question}">
                <figcaption>Drawn by AI for you question. It helps you picture the idea, but it is not an exact medical diagram.</figcaption>
                </figure>""")
        else:
            md("""
                <div class='plate-missing'>
                The illustration could not be drawn this time. The written answer on the left is not affected. 
                Ask again to retry the picture. 
                </div>""")

    md('<p class="note"> For learning only. This does not replace advice from a doctor or another health professtional.</p>')


# Hero 
md(f""" 
    <div class = "hero"> 
    <div class = "brand"><span class = "brand-mark">&#10010;</span>{APP_NAME}</div>
    <h1 class="hero-title">Ask one medical question. Get a clear answer and a picture.</h1>
    <p class="hero-text">Answers are written in plain language from the medical documents loaded into this site.
    An illustration is drawn for the same question, so you can read the idea and see it too.
    New here? Open the How it works tab.</p>
    </div>
""")

tab_ask, tab_how = st.tabs(['Ask a question', 'How it works'])

with tab_ask:
    st.session_state.setdefault("question","")
    st.session_state.setdefault("result", None)

    md('<h2 class = "section-title"> What would you like to understand? </h2>')
    st.text_area(
        "Your question",
        key = 'question',
        height=120,
        placeholder="Type your question in everyday words, for example: How does insuline lowe blood sugar?",
        label_visibility="collapsed",
    )

    md('<p class = "hint"> Not sure what to ask? Try one of these: </p>')
    example_cols = st.columns(len(EXAMPLES))
    for col, example in zip(example_cols, EXAMPLES):
        with col:
            st.button(example, key = f'example_{example}', on_click=use_example, args=(example, ))
    submitted = st.button("Get answer and illustration", type = 'primary')

    if submitted:
        question = st.session_state['question'].strip()
        if not question:
            st.warning("Type a qustion first then press get answer and illustration.")
        else:
            with st.spinner("Searching the medical documents and drawing the illustration. Please wait a little while."):
                try:
                    data = ask_backend(question)
                    st.session_state['result'] = {
                        'question' : question,
                        'answer' : data.get('answer', ''), 
                        'image' : data.get("image_base64"),
                    }
                except requests.exceptions.ConnectionError:
                    st.session_state['result'] = None
                    st.error("The back-end is not running. Open a terminal in the project folder.")
                except requests.exceptions.Timeout:
                    st.session_state['result'] = None
                    st.error("The back-end took too long to reply. Ask again If it keep happening." "check the FastAPI terminal for errors.")

                except requests.exceptions.HTTPError as error:
                    st.session_state['result'] = None
                    st.error(f"The back-end returned an error (status{error.response.status_code}).")

                except Exception as error:
                    st.session_state['result'] = None
                    st.error(f"Something went wrong: {error}")
    if st.session_state['result']:
        show_result(st.session_state['result'])


with tab_how:
    md("""
        <h2 class="section-title">How this site works</h2>
        <p class="lead">You type one medical question. The site sends it to two helpers at the same time:
        one writes an answer from the medical documents loaded here, the other draws an illustration.
        When both finish, you see them side by side.</p>
    """)
 
    md("""
        <div class="journey">
        <div class="station"><div class="station-num">1</div>
        <h3 class="sub-title">You ask</h3>
        <p>Type a question in everyday words on the Ask a question tab, then press the button.</p></div>
        <div class="station"><div class="station-num">2</div>
        <h3 class="sub-title">The question is shared</h3>
        <p>The back-end sends the same question to both helpers at once, so the wait is only as long as the slower one.</p></div>
        <div class="station"><div class="station-num">3</div>
        <h3 class="sub-title">Two helpers work</h3>
        <p>One searches the documents and writes the answer. The other draws the picture.</p></div>
        <div class="station"><div class="station-num">4</div>
        <h3 class="sub-title">You get both</h3>
        <p>The answer and the illustration appear together. If the picture fails, you still get the answer.</p></div>
        </div>
    """)
 
    md('<h2 class="section-title">What each helper does</h2>')
    col_one, col_two = st.columns(2, gap="medium")
 
    with col_one:
        md("""
            <div class="panel panel-text">
            <h3 class="sub-title">Helper 1: the written answer</h3>
            <p class="hint">Built only from the medical documents loaded into this site.</p>
            <ol>
            <li><strong>Search in two ways.</strong> One search finds passages that mean the same thing as your
            question, even when the words differ. The other finds passages that contain your exact words, such as a
            medicine or disease name. The two lists are then merged.</li>
            <li><strong>Keep the best passages.</strong> A second model reads your question next to each passage
            and keeps only the few that answer it best.</li>
            <li><strong>Write the answer.</strong> A language model running on Groq writes a plain-language answer
            using only those passages. If the documents do not cover your question, it says so instead of guessing.</li>
            </ol>
            </div>
        """)
 
    with col_two:
        md("""
            <div class="panel panel-image">
            <h3 class="sub-title">Helper 2: the illustration</h3>
            <p class="hint" style="color: var(--ink) !important;">Drawn for the same question by a separate image service.</p>
            <ol>
            <li><strong>Send the question.</strong> The back-end calls a small separate service (an MCP server)
            whose only job is to make images.</li>
            <li><strong>Draw the picture.</strong> That service asks an image model to create a clear, educational,
            non-graphic medical illustration of your question.</li>
            <li><strong>Return it.</strong> The picture is sent back and shown next to the written answer.</li>
            </ol>
            </div>
        """)
 
    md('<h2 class="section-title">Good to know</h2>')
    col_limits, col_use = st.columns(2, gap="large")
 
    with col_limits:
        md("""
            <ul class="plain">
            <li><strong>Answers are only as good as the documents.</strong> If the documents do not mention your
            topic, you get a message saying so rather than a guess.</li>
            <li><strong>Pictures are illustrations, not diagrams.</strong> AI draws them to help you picture an idea.
            Shapes and details can be wrong, so do not use them to study exact anatomy.</li>
            <li><strong>This site is for learning.</strong> It cannot diagnose or treat anything. Talk to a doctor
            or another health professional about symptoms or treatment.</li>
            </ul>
        """)
 
    with col_use:
        md("""
            <h3 class="sub-title">Who it helps</h3>
            <p><strong>Patients and families</strong> get plain-language explanations of conditions, tests and treatments.
            <strong>Students</strong> get a quick way to revise a topic and see it pictured.</p>
            <h3 class="sub-title">Asking good questions</h3>
            <p>Ask one thing at a time. Name the condition, organ or medicine. Start with How, What or Why,
            for example: <em>How does insulin lower blood sugar?</em></p>
        """)
 
    with st.expander("The technology behind it"):
        st.markdown(
            """
- **Streamlit** builds User Interface.
- **FastAPI** is the back-end. It receives your question and runs both helpers at the same time.
- **Pinecone** (meaning search) and **BM25** (keyword search) together search the medical documents.
- **A cross-encoder reranker** keeps the passages that fit your question best.
- **Groq** runs the language model that writes the answer.
- **MCP (Model Context Protocol)** connects the back-end to the separate image server.
- **Cloudflare** provides the image model that draws the illustration.
"""
        )

        
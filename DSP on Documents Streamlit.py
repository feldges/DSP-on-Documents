import dsp
import streamlit as st

colbert_server = 'http://127.0.0.1:8893/api/search' # You might have a different URL!

lm = dsp.GPT3(model='text-davinci-002', api_key='YOUR_API_KEY')
rm = dsp.ColBERTv2(url=colbert_server)

dsp.settings.configure(lm=lm, rm=rm)

# Build the prompt
# Provide instructions, questions, answers
Instructions = "Answer questions in one paragraph."
# Provide questions and answers
Question = dsp.Type(prefix="Question:", desc="${the question to be answered}")
Answer = dsp.Type(prefix="Answer:", desc="${an answer, with explanations}", format=dsp.format_answers)
# Provide the context
Context = dsp.Type(
    prefix="Context:\n",
    desc="${sources that may contain relevant content}",
    format=dsp.passages2text
)
# Provide a rationale
Rationale = dsp.Type(
    prefix="Rationale: Let's think step by step. Justify your answer.",
    desc="${a step-by-step deduction that identifies the correct response, which will be provided below}"
)
# Build the template with all these ingredients
qa_template = dsp.Template(instructions=Instructions, context=Context(), question=Question(), rationale=Rationale(), answer=Answer())

qa_pairs = [("Who is responsible to build highways?", ['The Confederation is responsible to build highways (Article 83).']),
         ("Do women have equal rights?", ["Yes, women have equal rights (Article 8)."]),
         ("What are the national languages?", ["The National Languages are German, French, Italian, and Romansh (Article 4)."]),
         ("Are citizen of any commune also Swiss citizen?", ["Yes, Swiss citizenship is granted to any person who is a citizen of a commune and of the Canton to which that commune belongs (Article 37)."]),
         ("What is the confederation's role regarding research?", ["The confederation's role in research is to promote scientific research and innovation and to establish, take over, or run research institutes (Article 64)."]),
         ("Who is responsible for the protection of the cultural heritage?", ["The Cantons are responsible for the protection of the cultural heritage (Article 78)."]),
         ("Who is responsible for the public transport?", ["The Confederation and the Cantons are responsible for the public transport (Article 81)."]),
         ("Who is responsible for the legislation around nuclear energy?", ["The Confederation is responsible for legislation in the field of nuclear energy (Article 90)."])]

qa_pairs = [dsp.Example(question=question, answer=answer) for question, answer in qa_pairs]

def retrieve_then_read_QA(question: str, qa_pairs: list = []) -> str:
    demos = dsp.sample(qa_pairs, k=8)
    passages = dsp.retrieve(question, k=5)
    example = dsp.Example(question=question, context=passages, demos=demos)
    example, completions = dsp.generate(qa_template)(example, stage='qa')
    return {"passages": passages, "answer": completions.answer}

question = st.text_input(label="Question about rights in the Swiss constitution. Ask and press enter")
if question:
    output = retrieve_then_read_QA(question, qa_pairs)
    answer = output["answer"]
    passages = output["passages"]
    t = ""
    for p in passages:
        t+="- "+p+"\n\n\n"
    st.write("**Answer:**")
    st.write(answer)
    st.write("**Evidence from the constitution:**")
    st.write(t)
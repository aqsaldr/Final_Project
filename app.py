# ============================================================
# SMARTPHONE ADVISOR
# Chatbot Perbandingan Produk untuk Tim Sales & Marketing
# Powered by LangChain + Groq + FAISS
# ============================================================
#
# CARA MENJALANKAN:
#   streamlit run app.py
#
# ============================================================

import streamlit as st
from rag_pipeline import build_rag_pipeline

# ── Konfigurasi Halaman ────────────────────────────────────────────────
st.set_page_config(
    page_title="Pekys Store",
    page_icon="👕", # Mengubah ikon HP menjadi ikon baju, bisa juga pakai "🛍️" atau "👗"
    layout="centered"
)

# ── Header ─────────────────────────────────────────────────────────────
st.title("🛒Pekys Store CS")
st.caption(
    "AI Customer Service Assistant Pekys Store"
    "Helps answer questions about clothing catalogs, innovative materials, sizing guides, and shipping."
)

# ── Load RAG Pipeline ──────────────────────────────────────────────────
# Menggunakan st.cache_resource agar pipeline hanya dibangun sekali.
# Tanpa ini, pipeline akan dibangun ulang setiap ada interaksi pengguna.
@st.cache_resource(show_spinner=False)
def load_pipeline():
    return build_rag_pipeline()

# Tampilkan proses loading kepada pengguna
if "pipeline_loaded" not in st.session_state:
    with st.status("Loading AI system...", expanded=True) as status:
        st.write("Reading product catalog...")
        st.write("Building vector store...")
        st.write("Initializing language model...")
        chain, num_chunks = load_pipeline()
        st.session_state.chain = chain
        st.session_state.num_chunks = num_chunks
        st.session_state.pipeline_loaded = True
        status.update(
            label=f"System ready! {num_chunks} document chunks successfully indexed.",
            state="complete"
        )

chain = st.session_state.chain

# ── Inisialisasi Riwayat Chat ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Tampilkan Contoh Pertanyaan (hanya saat belum ada chat) ───────────
if not st.session_state.messages:
    st.info(
        "**Example questions you can ask:**\n\n"
        "- What's the difference between Aerochill and ThermoWarm materials?\n"
        "- Are there any Big or Oversize sizes?\n"
        "- How do I care for Aerochill clothing?\n"
        "- What clothes are best to wear in hot weather?\n"
        "- If the size doesn't fit, can the item be exchanged?\n"
        "- Are there any bundling promotions or discounts on first-time buyers?"
    )
    
# ── Tampilkan Riwayat Chat ─────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Input Pengguna ─────────────────────────────────────────────────────
if user_input := st.chat_input("Ask something about clothing products..."):

    # Simpan dan tampilkan pesan pengguna
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate jawaban dari RAG chain
    with st.chat_message("assistant"):
        with st.spinner("Searching for information in the catalog..."):
            result = chain.invoke({"query": user_input})
            answer = result["result"]
            source_docs = result["source_documents"]

        st.markdown(answer)

        # Tampilkan referensi dokumen sumber (bisa di-collapse)
        with st.expander("Look Catalog Reference"):
            for i, doc in enumerate(source_docs, 1):
                st.markdown(f"**Referensi {i}:**")
                st.text(doc.page_content[:300] + "...")
                st.divider()

    # Simpan jawaban ke riwayat
    st.session_state.messages.append({"role": "assistant", "content": answer})


# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📋About Pekys AI")
    st.markdown(
        "Pekys Store Assistant is an AI-powered smart chatbot designed specifically for loyal Pekys Store customers."
        "No more waiting for a response!"
        "This app is ready to assist you 24/7 to find the best men's and women's"
        "clothing with our exclusive innovative materials, Aerochill (Anti-Heat) and ThermoWarm (Anti-Cold)."
        "Happy Shopping"
    )

    st.divider()

    st.subheader("👕 Product Category")
    st.markdown(
        "1. ​​**T-Shirts & Shirts** (Basic, Oversized, Flannel)\n\n"
        "2. **Aerochill Collection** (Heat-Resistant Material)\n\n"
        "3. **Hoodies & Sweaters** (Basic, Zipper, Knit)\n\n"
        "4. **ThermoWarm Collection** (Cold-Resistant Material)\n\n"
        "5. **Jackets** (Bomber, Windbreaker, Denim)\n\n"
        "6. **Pants** (Chino, Jogger, Cargo, Jeans)"
    )


    st.divider()

    if st.button("🔄 Reset conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

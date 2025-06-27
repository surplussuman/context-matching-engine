import streamlit as st
import os
from utils.audio_utils import extract_audio, transcribe_audio
from utils.db_utils import insert_transcript, init_db, fetch_all_transcripts
from utils.video_utils import download_video_from_url
import difflib

# Initialize DB on startup
init_db()

# Set Streamlit page config
st.set_page_config(page_title="DMX CME", layout="wide")

# Sidebar navigation
st.sidebar.title("Context Matching Engine")
app_mode = st.sidebar.radio("Go to", ["Upload Content", "Check Similarity", "View Uploaded Contents"])

# Create upload folder
os.makedirs("data/uploads", exist_ok=True)

if app_mode == "Upload Content":
    st.header("Upload Educational Video")
    st.markdown("Upload a video file (max 20 MB). Optionally edit the transcript before saving.")

    uploaded_file = st.file_uploader("Upload video file", type=["mp4", "mov", "mkv", "avi"])

    custom_filename = st.text_input("Optional: Enter a name for this video (used as identifier)")

    if uploaded_file:
        # Save uploaded video
        file_path = os.path.join("data/uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"Uploaded: {uploaded_file.name}")

        # Store path in session for later access
        st.session_state["uploaded_video_path"] = file_path
        st.session_state["video_name"] = custom_filename.strip() if custom_filename else uploaded_file.name

        # Button to trigger transcription process
        if st.button("🚀 Process Video"):
            # Step 1: Extract Audio
            with st.spinner("Extracting audio..."):
                audio_path = extract_audio(file_path, output_audio_path="data/audio.wav")

            if audio_path:
                # Step 2: Transcribe Audio
                with st.spinner("Transcribing audio..."):
                    transcript = transcribe_audio(audio_path)

                if transcript:
                    st.session_state["transcript"] = transcript
                    st.success("Transcription complete!")
                else:
                    st.error("Transcription failed.")
            else:
                st.error("Audio extraction failed.")

    if "transcript" in st.session_state:
        edited_transcript = st.text_area("Edit Transcript (optional):", value=st.session_state["transcript"], height=300)

        if st.button("💾 Save Transcript to Database"):
            insert_transcript(st.session_state["video_name"], edited_transcript)
            st.success(f"Transcript for '{st.session_state['video_name']}' saved to database.")

elif app_mode == "Check Similarity":
    st.header("🔍 Check Video Similarity")
    st.markdown("Paste a video URL (YouTube, Facebook, etc.). We'll extract its content and match it against existing videos.")

    url = st.text_input("Paste the video URL here")

    if st.button("🚀 Process and Check Similarity") and url:
        with st.spinner("Downloading video..."):
            downloaded_path = download_video_from_url(url)

        if downloaded_path and os.path.exists(downloaded_path):
            st.success(f"Video downloaded: {os.path.basename(downloaded_path)}")

            with st.spinner("Extracting and transcribing audio..."):
                audio_path = extract_audio(downloaded_path, output_audio_path="data/temp_url_audio.wav")
                if audio_path:
                    transcript = transcribe_audio(audio_path)
                    if transcript:
                        st.success("Transcript extracted from URL!")

                        # Compare with all saved transcripts in DB
                        st.markdown("---")
                        st.subheader("🧠 Similarity Scores")
                        db_transcripts = fetch_all_transcripts()

                        if not db_transcripts:
                            st.warning("No uploaded content found in database.")
                        else:
                            for record in db_transcripts:
                                similarity_ratio = difflib.SequenceMatcher(
                                    None, record["transcript"], transcript
                                ).ratio()

                                percentage = round(similarity_ratio * 100, 2)

                                with st.expander(f"📹 {record['video_name']} - Similarity: {percentage}%"):
                                    st.text_area("Transcript from DB:", record["transcript"], height=200, disabled=True)
                                    st.text_area("Transcript from URL:", transcript, height=200, disabled=True)
                    else:
                        st.error("Transcription failed.")
                else:
                    st.error("Audio extraction failed.")
        else:
            st.error("Failed to download video from URL.")


elif app_mode == "View Uploaded Contents":
    st.header("📄 Uploaded Video Transcripts")
    st.markdown("Browse the content you've uploaded so far.")

    def format_transcript(transcript):
        import re
        segments = re.findall(r'\[\d+\.\d+s\s-\s\d+\.\d+s\]:.*?(?=\[\d+\.\d+s\s-\s\d+\.\d+s\]:|$)', transcript, re.DOTALL)
        return "\n".join(segment.strip() for segment in segments)

    records = fetch_all_transcripts()

    if records:
        for record in records:
            with st.expander(f"📹 {record['video_name']} (Uploaded on {record['upload_time'].strftime('%Y-%m-%d %H:%M:%S')})"):
                formatted = format_transcript(record['transcript'])
                # Unique key for each transcript widget
                st.text_area("Transcript", value=formatted, height=300, disabled=True,
                             key=f"{record['video_name']}_{record['upload_time']}")
    else:
        st.info("No transcripts found yet. Upload some content first.")


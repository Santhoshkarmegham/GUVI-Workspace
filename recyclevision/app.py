"""Streamlit entry point; image preview is available before model training."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from PIL import Image, UnidentifiedImageError
import streamlit as st
from recyclevision.config import CLASSES

st.set_page_config(page_title='RecycleVision', page_icon='♻️', layout='wide')
st.title('♻️ RecycleVision')
st.caption('Garbage Image Classification Using Deep Learning')
st.info('Project setup is ready. Download the dataset and train a model before classification is available.')
st.subheader('Waste categories')
st.write(' · '.join(label.title() for label in CLASSES))
upload = st.file_uploader('Upload a waste image to preview', type=['jpg', 'jpeg', 'png', 'webp'])
if upload is not None:
    try:
        with Image.open(upload) as image:
            image.load()
            st.image(image.convert('RGB'), caption='Uploaded image', width=400)
        st.warning('No trained model is available. This preview does not predict a waste category.')
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError):
        st.error('This file could not be opened safely as an image. Try another image.')
with st.expander('Dataset setup'):
    st.markdown('Download the six-class dataset from [Kaggle](https://www.kaggle.com/datasets/asdasdasasdas/garbage-classification), extract it into `data/raw/`, then run `python scripts/profile_data.py`. Keep the class folders intact.')

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Symlink fonts to where _find_font() looks (it checks direct children, not subdirs)
RUN ln -s /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf /usr/share/fonts/truetype/DejaVuSans-Bold.ttf && \
    ln -s /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf /usr/share/fonts/truetype/DejaVuSans.ttf

WORKDIR /app

RUN pip install --no-cache-dir Flask gunicorn Pillow python-pptx

COPY scout_awards/ scout_awards/
COPY award_images.json prefetch_images.py ./
COPY images/rank_*.png images/

# Download all badge images at build time
RUN python prefetch_images.py

COPY app.py .
COPY templates/ templates/

ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 120 app:app

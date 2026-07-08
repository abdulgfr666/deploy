# Dashboard Sales Report

Proyek ini adalah Dashboard interaktif untuk pelaporan penjualan yang dikembangkan menggunakan **Streamlit** (Python) dan juga mendukung *build* statis (HTML, CSS, JS) menggunakan Plotly.js. Tampilan dashboard telah dipercantik dengan kustomisasi CSS dan **Font Awesome**.

## Prasyarat

Pastikan Anda sudah menginstal Python (minimal versi 3.8+).

## 1. Install Dependencies

Untuk menginstal semua pustaka yang dibutuhkan, jalankan perintah berikut di terminal:

```bash
pip install -r requirements.txt
```
*(Catatan: Jika Anda menggunakan Windows dan `pip` tidak dikenali, gunakan `py -m pip install -r requirements.txt`)*

## 2. Menjalankan Dashboard Streamlit

Untuk melihat dashboard dalam versi interaktif Streamlit yang berjalan di atas server Python, jalankan:

```bash
streamlit run layout.py
```
*(Jika `streamlit` tidak dikenali, gunakan `py -m streamlit run layout.py`)*

Dashboard akan otomatis terbuka di browser pada URL **http://localhost:8501**.

## 3. Build Dashboard (Ekspor ke HTML, CSS, JS Statis)

Proyek ini memiliki fitur khusus untuk mengekspor (build) keseluruhan layout dashboard menjadi file *native web* (HTML, CSS, JS) murni yang tidak membutuhkan server Python untuk berjalan. Ini sangat berguna jika Anda ingin mempublikasikan dashboard di layanan *hosting* statis gratis seperti GitHub Pages, Netlify, atau Vercel.

Untuk melakukan proses *build*, jalankan:

```bash
python build.py
```

Perintah ini akan secara otomatis:
- Memproses data CSV (seperti di `layout.py`).
- Mengubah objek grafik Plotly menjadi format JSON.
- Menghasilkan (`generate`) file `index.html`, `style.css`, dan `script.js` ke dalam folder `public/`.

## 4. Menjalankan Server Publik (Pratinjau HTML Statis)

Setelah proses *build* selesai, Anda bisa mempratinjau hasilnya di lokal dengan menjalankan server HTTP bawaan Python.

Dari *root* direktori proyek, jalankan:

```bash
python -m http.server 8000 --directory public
```

Buka **http://localhost:8000** di browser Anda untuk melihat versi *live* HTML/CSS/JS dari dashboard tersebut!
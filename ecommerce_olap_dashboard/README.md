# Global E-Commerce OLAP Dashboard

Project ini adalah implementasi siap pakai untuk proposal **Pemodelan Data / OLAP E-Commerce** dengan arsitektur dual-database:

- **PostgreSQL** untuk data relasional: `customers`, `products`, `orders`
- **MongoDB** untuk data semi-terstruktur: `transaction_logs`, `shipping_details`
- **Streamlit + Plotly** untuk dashboard visualisasi interaktif

Dataset yang digunakan: `data/global_ecommerce_sales.csv` dengan 2.000 transaksi.

---

## 1. Rumusan Masalah

### Problem 1 — Analisis Profitabilitas
Bagaimana pola profitabilitas berdasarkan kategori produk, segmen pelanggan, dan wilayah geografis, serta faktor apa saja yang paling berpengaruh terhadap margin keuntungan?

### Problem 2 — Analisis Tren Penjualan
Bagaimana tren penjualan bulanan dan seasonal, serta produk atau kategori mana yang menunjukkan performa terbaik dan terburuk dalam periode tertentu?

### Problem 3 — Analisis Efektivitas Diskon dan Pengiriman
Bagaimana efektivitas pemberian diskon dan efisiensi biaya pengiriman terhadap margin keuntungan transaksi berdasarkan kategori produk, wilayah, dan segmen pelanggan?

---

## 2. Struktur Project

```text
ecommerce_olap_dashboard/
├── app.py                         # Dashboard Streamlit
├── docker-compose.yml             # PostgreSQL + MongoDB
├── requirements.txt               # Dependency Python
├── .env.example                   # Template konfigurasi database
├── run_windows.bat                # Auto-run untuk Windows
├── run_mac_linux.sh               # Auto-run untuk macOS/Linux
├── data/
│   └── global_ecommerce_sales.csv # Dataset utama
├── src/
│   ├── config.py                  # Konfigurasi environment
│   ├── database.py                # Koneksi PostgreSQL dan MongoDB
│   └── etl.py                     # ETL CSV ke PostgreSQL + MongoDB
└── sql/
    ├── schema.sql                 # DDL PostgreSQL
    ├── analytics_queries.sql      # Query analitik PostgreSQL
    └── mongo_aggregations.js      # Pipeline agregasi MongoDB
```

---

## 3. Cara Menjalankan

### Opsi A — Windows

Pastikan sudah install:

1. Python 3.10+
2. Docker Desktop

Lalu buka terminal di folder project dan jalankan:

```bash
run_windows.bat
```

### Opsi B — macOS / Linux

Pastikan sudah install:

1. Python 3.10+
2. Docker Desktop / Docker Engine

Lalu jalankan:

```bash
./run_mac_linux.sh
```

### Opsi C — Manual

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows
pip install -r requirements.txt
docker compose up -d
python -m src.etl
streamlit run app.py
```

Dashboard akan terbuka di browser melalui URL yang diberikan Streamlit, biasanya:

```text
http://localhost:8501
```

---

## 4. Output Dashboard

### Problem 1 — Profitabilitas

Visualisasi yang tersedia:

- Total profit per kategori produk
- Kontribusi profit per segmen pelanggan
- Heatmap profit margin berdasarkan region dan customer segment
- Ranking produk berdasarkan total profit dan profit margin

### Problem 2 — Tren Penjualan

Visualisasi yang tersedia:

- Line chart monthly sales dan monthly profit
- Tren penjualan kategori produk per bulan
- Seasonal pattern berdasarkan bulan
- Top 10 dan bottom 10 produk berdasarkan profit

### Problem 3 — Diskon & Pengiriman

Visualisasi yang tersedia:

- Profit margin berdasarkan level diskon
- Scatter plot shipping-to-sales ratio terhadap profit margin
- Scatter plot level transaksi dengan warna berdasarkan diskon
- Heatmap region × product category
- Tabel area risiko margin rendah

---

## 5. Pembagian Database

### PostgreSQL

Data yang masuk ke PostgreSQL:

- `customers`: customer name, segment, country, region
- `products`: product category, product name, unit price
- `orders`: order date, customer_id, product_id, quantity, total sales, profit

### MongoDB

Data yang masuk ke MongoDB:

- `transaction_logs`: order_id, payment method, discount percent
- `shipping_details`: order_id, country, region, shipping cost

Kedua database dihubungkan melalui field `order_id`.

---

## 6. Catatan Teknis

Metrik yang digunakan:

```text
Profit Margin (%) = Profit / Total Sales * 100
Shipping-to-Sales Ratio (%) = Shipping Cost / Total Sales * 100
```

Project ini sengaja dibuat dengan pemisahan PostgreSQL dan MongoDB agar sesuai dengan kebutuhan tugas yang meminta penggunaan SQL dan NoSQL secara bersamaan.

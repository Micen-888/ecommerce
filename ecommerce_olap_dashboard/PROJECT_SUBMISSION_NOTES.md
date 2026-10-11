# Catatan Penyerahan Project

Project ini sudah dirancang sebagai aplikasi dashboard analitik yang dapat langsung dijalankan oleh pembimbing.

## Ringkasan Implementasi

1. Dataset CSV dibaca oleh script ETL.
2. Data dinormalisasi ke PostgreSQL menjadi `customers`, `products`, dan `orders`.
3. Data semi-terstruktur dimasukkan ke MongoDB menjadi `transaction_logs` dan `shipping_details`.
4. Dashboard Streamlit membaca data dari kedua database.
5. Data digabungkan berdasarkan `order_id` untuk menghasilkan visualisasi OLAP.

## Alasan Revisi Problem 3

Rumusan lama yang berfokus pada metode pembayaran kurang kuat karena dataset hanya menyediakan kategori metode pembayaran tanpa data fee, settlement time, refund, chargeback, atau status pembayaran.

Rumusan baru lebih relevan karena dataset memiliki kolom diskon, biaya pengiriman, total sales, dan profit. Oleh karena itu, analisis efektivitas diskon dan efisiensi biaya pengiriman lebih layak digunakan sebagai rumusan masalah utama ketiga.

## Nilai Tambah Dashboard

- Memiliki filter OLAP interaktif.
- Mendukung drill-down secara praktis melalui filter region, country, segment, category, dan periode.
- Menampilkan metrik profit margin dan shipping-to-sales ratio.
- Dapat mengekspor hasil filter ke CSV.

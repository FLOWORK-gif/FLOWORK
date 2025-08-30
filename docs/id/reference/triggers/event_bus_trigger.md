# Pemicu Event Bus Internal

> Menciptakan alur kerja yang reaktif. Trigger ini mendengarkan 'sinyal' atau 'event' yang diterbitkan oleh modul lain, memungkinkan Anda membuat sistem yang saling terhubung dan cerdas.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `event_bus_trigger` |
| Tier | Free |
| Version | 1.0.0 |
| Author | Flowork Core |

## How to Use
**Konsep:**
Event Bus adalah papan pengumuman sentral. Satu modul ('Publisher') bisa meneriakkan sebuah pesan (event), dan trigger ini ('Subscriber') akan mendengarnya jika tertarik dengan topik pesan tersebut.

**Cara Penggunaan:**
1. Dalam satu workflow, gunakan modul 'Publish Event' untuk mengirim sinyal saat tugas penting selesai. Beri nama event yang jelas, misal: `PROSES_A_SELESAI`.
2. Di halaman Trigger Manager, buat Aturan baru menggunakan trigger ini.
3. Di propertinya, masukkan nama event yang sama persis (`PROSES_A_SELESAI`).
4. Pilih workflow lain yang ingin Anda jalankan sebagai respons.

**Contoh Optimasi:**
- **Workflow Berantai:** Jalankan alur 'Proses B' secara otomatis HANYA JIKA alur 'Proses A' telah selesai dengan sukses dan mengirim event.
- **Notifikasi Terpusat:** Beberapa workflow bisa menerbitkan event `KIRIM_NOTIFIKASI_PENTING`, dan satu workflow yang dipicu oleh event ini bertugas mengirimkannya ke Telegram.

## API Reference

::: triggers.event_bus_trigger.listener

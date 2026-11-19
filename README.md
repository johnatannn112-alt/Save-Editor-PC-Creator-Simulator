# Save Editor v3

Editor save untuk game simulasi mining PC (Unity IL2CPP). File `v3.dat` memakai .NET BinaryFormatter tanpa enkripsi, jadi nilainya bisa diedit langsung.

## Versi web (`index.html`)
Buka `index.html` di browser (atau lewat GitHub Pages), pilih `v3.dat`, ubah nilainya, lalu simpan. Semua diproses di perangkatmu.

Tombol "Unduh v3.dat" mengunduh file hasil edit langsung dengan nama v3.dat.

## Versi Python
```
python3 save_editor.py v3.dat                      # tampilkan semua field
python3 save_editor.py v3.dat Money=500000 Level=15 -o v3_edit.dat
```
`save_editor.py` dan `nrbf.py` harus berada di folder yang sama. Hanya nilai angka dan true/false di class `Player` yang diubah, dan ukuran file tidak berubah.

## Sebelum menimpa save
1. Salin `v3.dat` asli sebagai cadangan.
2. Tutup game sepenuhnya.
3. Timpa `v3.dat`, lalu buka game.

Format bisa berubah kalau game diupdate (misalnya jadi `v4`).

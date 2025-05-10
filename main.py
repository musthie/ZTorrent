import re
import string
import itertools as it
from tkinter import filedialog
import customtkinter

# Bencode encode fonksiyonu
def encode(obj):
    if isinstance(obj, int):
        return b"i" + str(obj).encode() + b"e"
    elif isinstance(obj, bytes):
        return str(len(obj)).encode() + b":" + obj
    elif isinstance(obj, str):
        return encode(obj.encode("ascii"))
    elif isinstance(obj, list):
        return b"l" + b"".join(map(encode, obj)) + b"e"
    elif isinstance(obj, dict):
        if all(isinstance(i, bytes) for i in obj.keys()):
            items = list(obj.items())
            items.sort()
            return b"d" + b"".join(map(encode, it.chain(*items))) + b"e"
        else:
            raise ValueError("dict keys should be bytes")
    raise ValueError("Allowed types: int, bytes, list, dict; not %s", type(obj))


# Bencode decode fonksiyonu
def decode(s):
    def decode_first(s):
        if s.startswith(b"i"):
            match = re.match(b"i(-?\\d+)e", s)
            return int(match.group(1)), s[match.span()[1]:]
        elif s.startswith(b"l") or s.startswith(b"d"):
            l = []
            rest = s[1:]
            while not rest.startswith(b"e"):
                elem, rest = decode_first(rest)
                l.append(elem)
            rest = rest[1:]
            if s.startswith(b"l"):
                return l, rest
            else:
                return {i: j for i, j in zip(l[::2], l[1::2])}, rest
        elif any(s.startswith(i.encode()) for i in string.digits):
            m = re.match(b"(\\d+):", s)
            length = int(m.group(1))
            rest_i = m.span()[1]
            start = rest_i
            end = rest_i + length
            return s[start:end], s[end:]
        else:
            raise ValueError("Malformed input.")

    if isinstance(s, str):
        s = s.encode("ascii")

    ret, rest = decode_first(s)
    if rest:
        raise ValueError("Malformed input.")
    return ret


# Dosya seçme fonksiyonu
def file_select():
    file_way = filedialog.askopenfilename(title="Bir dosya seçin", filetypes=[("Torrent Dosyaları", "*.torrent")])

    if file_way:
        try:
            with open(file_way, 'rb') as file:
                dosya_icerik = file.read()

            result = decode(dosya_icerik)
            print(result)

        except Exception as e:
            print(f"Hata: {e}")


# Uygulama arayüzü
app = customtkinter.CTk()
app.geometry("600x400")
app.title("ZiyTorrent")

# Başlıklar
label1 = customtkinter.CTkLabel(app, text="ZiyTorrent", font=("Comic Sans MS", 25))
label1.pack(pady=10, anchor="w")

label2 = customtkinter.CTkLabel(app, text="Datanızı Çalıyoruz", font=("Comic Sans MS", 20))
label2.pack(pady=10, anchor="w")

# Buton
button_dosya_sec = customtkinter.CTkButton(app, text="Dosya Seç", command=file_select)
button_dosya_sec.pack(pady=20)

app.mainloop()

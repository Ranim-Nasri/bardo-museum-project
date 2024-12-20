import qrcode

url = "https://maps.app.goo.gl/p43CTTvDnkfr89LC9"

qr = qrcode.make(url)

qr.save("static/museum_tour_qr.png")

print("QR code generated!")
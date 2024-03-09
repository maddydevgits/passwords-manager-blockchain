import time 
import pyotp 
import qrcode 

k = pyotp.random_base32()
secret_key = "MakeSkilledJoinsKITSCSE"

totp_auth = pyotp.totp.TOTP( 
secret_key).provisioning_uri( 
name='Dwaipayan_Bandyopadhyay', 
issuer_name='GeeksforGeeks') 

print(totp_auth)

qrcode.make(totp_auth).save("qr_auth.png") 
totp_qr = pyotp.TOTP(secret_key)


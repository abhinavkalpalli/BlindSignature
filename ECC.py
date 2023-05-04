

import pickle
import ecdsa

def signature(fn,id):
# Generate private/public key pair
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) # private key
    vk = sk.verifying_key # public key
    # Serialize and store private key to file


    vk_str = pickle.dumps(vk)
    with open("static/publickey/"+str(id)+".pickle", "wb") as f:
        f.write(vk_str)


    with open(fn, "rb") as imageFile:
        message = imageFile.read()


        signature = sk.sign(message)


        signature_str = pickle.dumps(signature)
        with open("static/signature/"+str(id)+".pickle", "wb") as f:
            f.write(signature_str)

def validate_sign(fn,id):


    try:
        with open("static/signature/"+str(id)+".pickle", "rb") as f:
            signature_str1 = f.read()
        signature1 = pickle.loads(signature_str1)


        with open("static/publickey/"+str(id)+".pickle", "rb") as f:
            vk_str1 = f.read()
        vk1 = pickle.loads(vk_str1)

        with open(fn, "rb") as imageFile:
            message = imageFile.read()
        x= vk1.verify(signature1, message)
        return x
    except:
        return False

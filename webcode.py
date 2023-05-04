import os

import functools
from flask import *
from werkzeug.utils import secure_filename

from src.db import *
from src.AES import *
from src.ECC import *
app=Flask(__name__)

app.secret_key="123"

@app.route('/')
def login():
    return  render_template("loginindex.html")

def login_required(func):
    @functools.wraps(func)
    def secure_function():
        if "lid" not in session:
            return render_template('loginindex.html')
        return func()

    return secure_function


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



@app.route('/logincode',methods=['post'])
def logincode():
    uname=request.form['textfield']
    pwrd=request.form['textfield2']
    qry="SELECT * FROM `login` WHERE `username`=%s AND `password`=%s"
    val=(uname,pwrd)
    res=selectone(qry,val)
    if res is None:
        return '''<script>alert('invalid ');window.location="/"</script>'''
    elif res['type'] == 'manufacture':

        session['lid']=res['lid']
        return '''<script>alert('Welcome To Manufacture Home...');window.location="/manufacturehome"</script>'''
    elif res['type'] =='agency':
        session['lid']=res['lid']

        return '''<script>alert('Welcome To Agency Home...');window.location="/agencyhome"</script>'''
    elif res['type'] == 'shop':
        session['lid']=res['lid']

        return '''<script>alert('Welcome To Shop Home...');window.location="/shophome"</script>'''
    else:
            return '''<script>alert('invalid username or password');window.location="/"</script>'''




@app.route('/agencyreg',methods=['post','get'])
def agencyreg():
    return render_template("agencyregindex.html")

@app.route('/register',methods=['post','get'])
def register():
    fname=request.form['textfield']
    lname=request.form['textfield7']
    place=request.form['textfield2']
    post=request.form['textfield9']
    pin=request.form['textfield10']

    phn = request.form['textfield3']
    email = request.form['textfield4']
    username=request.form['textfield5']
    password= request.form['textfield6']
    r = selectone("SELECT * FROM agency  WHERE email=%s", (email))
    if r:
        return '''<script>alert("Already Exist"); window.location='/'</script>'''
    else:
        qry="insert into login values(null,%s,%s,'pending') "
        val=(username,password)
        id=iud(qry,val)
        qry1="INSERT INTO `agency` VALUES(NULL,%s,%s,%s,%s,%s,%s,%s,%s)"
        val1=(str(id),fname,lname,place,post,pin,email,phn)
        iud(qry1,val1)
        return '''<script>alert("added succcessfully");window.location="/"</script>'''


@app.route('/shopreg',methods=['post','get'])
def shopreg():
    return render_template("shopregindex.html")

@app.route('/Shopregister1',methods=['post','get'])
def Shopregister1():
    name=request.form['textfield']

    place=request.form['textfield2']
    post=request.form['textfield9']
    pin=request.form['textfield10']

    phn = request.form['textfield3']
    email = request.form['textfield4']
    username=request.form['textfield5']
    password= request.form['textfield6']
    r = selectone("SELECT * FROM shop  WHERE email=%s", (email))
    if r:
        return '''<script>alert("Already Exist"); window.location='/'</script>'''
    else:
        qry="insert into login values(null,%s,%s,'shop') "
        val=(username,password)
        id=iud(qry,val)
        qry1="INSERT INTO `shop` VALUES(NULL,%s,%s,%s,%s,%s,%s,%s)"
        val1=(str(id),name,place,post,pin,phn,email)
        iud(qry1,val1)
        return '''<script>alert("added succcessfully");window.location="/"</script>'''





####################################################################



@app.route('/agencyhome',methods=['post','get'])
@login_required
def agencyhome():
    return render_template("AGENCY/AGENCYHOME.html")

@app.route('/requeststatus_agent',methods=['post','get'])
@login_required
def requeststatus_agent():
    qry="SELECT `productrequest`.*,`products`.`name`,`image` FROM `productrequest` JOIN `products` ON `productrequest`.`pid`=`products`.`pid` WHERE `productrequest`.`lid`=%s"
    res=selectall2(qry,session['lid'])

    return render_template("AGENCY/REQUEST STATUS _AGENT.html",val=res)

@app.route('/viewproduct',methods=['post','get'])
@login_required
def viewproduct():
    qry="select * from products"
    res=selectall(qry)
    return render_template("AGENCY/VIEW PRODUCT.html",val=res)


@app.route('/sendquantityforrequest',methods=['post','get'])
@login_required
def sendquantityforrequest():
    id=request.args.get('id')
    session['proid']=id

    return render_template("AGENCY/requestquantity.html")



@app.route('/sendrequest_agency',methods=['post','get'])
@login_required
def sendrequest_agency():
    qty=request.form['textfield']
    qry="select * from products where pid=%s"
    res = selectone(qry,session['proid'])
    if int(qty) < int(res['qty']):
        qry="insert into productrequest values(null,%s,%s,'pending',%s,curdate())"
        val=(session['lid'],session['proid'],qty)
        iud(qry,val)
        return '''<script>alert("request sended...");window.location="/agencyhome#about"</script>'''
    else:
        return '''<script>alert("stock is less");window.location="/agencyhome#about"</script>'''






@app.route('/viewrequest',methods=['post','get'])
@login_required
def viewrequest():
    qry="SELECT `requestproduct_shop`.*,`shop`.* ,`products`.`name`as pname,`products`.`image` FROM `products` JOIN `requestproduct_shop` ON `products`.`pid`=`requestproduct_shop`.`pid`  JOIN `shop` ON `shop`.`lid`=`requestproduct_shop`.`lid` JOIN `productrequest` ON `productrequest`.`pid`=`products`.`pid` WHERE `productrequest`.`lid`=%s"
    res=selectall2(qry,session['lid'])
    return render_template("AGENCY/VIEW REQUEST FROM SHOP.html",val=res)


@app.route('/acceptshopreq',methods=['post','get'])
@login_required
def acceptshopreq():
    id=request.args.get('id')
    print(id,"iddddddddddddddddddddddddddd")
    qry="update requestproduct_shop set status='accept' where reqid=%s"
    iud(qry,id)

    qry = "SELECT `pid`,`qty` FROM `productrequest` WHERE `reqid`=%s"
    res = selectone(qry,id)


    q="update products set qty=qty-%s where pid=%s"
    iud(q,(res['qty'], res['pid']))


    return '''<script>alert("accepted..");window.location='/viewrequest#about'</script>'''


@app.route('/rejectshopreq',methods=['post','get'])
@login_required
def rejectshopreq():
    id = request.args.get('id')
    qry = "update requestproduct_shop set status='reject' where reqid=%s"
    iud(qry, id)
    return '''<script>alert("rejected..");window.location='/viewrequest#about'</script>'''




########################manufacture################################

@app.route('/addproduct',methods=['post','get'])
@login_required
def addproduct():
    return render_template("MANUFACTURE/ADD PRODUCT.html")


@app.route('/addproduct1',methods=['post','get'])
@login_required
def addproduct1():
    pname=request.form['textfield']
    photo=request.files['file']
    fs=secure_filename(photo.filename)

    photo.save(os.path.join('static/uploads',fs))
    key="myencryptionkey"
    with open(os.path.join('static/uploads',fs), "rb") as imageFile:
        stri = base64.b64encode(imageFile.read()).decode('utf-8')
        enc1 = encrypt(stri,key ).decode('utf-8')

        fh = open(os.path.join('static/uploads',fs), "wb")
        fh.write(base64.b64decode(enc1))
        fh.close()

    price=request.form['textfield2']
    description=request.form['textarea']
    qty=request.form['textfield4']
    qry="INSERT INTO `products` VALUES(NULL,%s,%s,%s,%s,%s)"
    val=(pname,fs,price,description,qty)
    pid=iud(qry,val)
    signature(os.path.join('static/uploads', fs),pid)

    return '''<script>alert("product added");window.location='/manageproduct#about'</script>'''

@app.route('/deleteproduct',methods=['post','get'])
@login_required
def deleteproduct():
    id=request.args.get('id')
    qry="delete from products where pid=%s"
    iud(qry,id)
    return '''<script>alert("product deleted");window.location='/manageproduct#about'</script>'''




@app.route('/editproduct',methods=['post','get'])
@login_required
def editproduct():
    id=request.args.get('id')
    session['pid']=id
    qry="select * from products where pid=%s"
    res=selectone(qry,id)
    return render_template("MANUFACTURE/EDIT PRODUCT.html",val=res)


@app.route('/editproduct1',methods=['post','get'])
@login_required
def editproduct1():
    try:
        pname=request.form['textfield']
        photo=request.files['file']
        fs=secure_filename(photo.filename)
        photo.save(os.path.join('static/uploads',fs))
        price=request.form['textfield2']
        description=request.form['textarea']
        qty=request.form['textfield4']
        qry="UPDATE `products` SET `name`=%s,`image`=%s,`price`=%s,`description`=%s,`qty`=%s WHERE `pid`=%s"
        val=(pname,fs,price,description,qty,session['pid'])
        iud(qry,val)
        return '''<script>alert("product updated");window.location='/manageproduct#about'</script>'''
    except:
        pname = request.form['textfield']

        price = request.form['textfield2']
        description = request.form['textarea']
        qty = request.form['textfield4']
        qry ="UPDATE `products` SET `name`=%s,`price`=%s,`description`=%s,`qty`=%s WHERE `pid`=%s"
        val = (pname, price, description, qty,session['pid'])
        iud(qry, val)
        return '''<script>alert("product updated");window.location='/manageproduct#about'</script>'''


@app.route('/approveagency',methods=['post','get'])
@login_required
def approveagency():
    qry="SELECT `agency`.*,`login`.type FROM `agency` JOIN  `login` ON `login`.`lid`=`agency`.`lid`"
    res=selectall(qry)
    return render_template("MANUFACTURE/APPROVE AGENCY.html",val=res)



@app.route('/acceptagency',methods=['post','get'])
@login_required
def acceptagency():
    id=request.args.get('id')
    qry="update login set type='agency' where lid=%s"
    iud(qry,id)
    return '''<script>alert("accepted..");window.location='/approveagency#about'</script>'''


@app.route('/rejectagency',methods=['post','get'])
@login_required
def rejectagency():
    id = request.args.get('id')
    qry = "update login set type='reject' where lid=%s"
    iud(qry, id)
    return '''<script>alert("rejected..");window.location='/approveagency#about'</script>'''






@app.route('/manageproduct',methods=['post','get'])
@login_required
def manageproduct():
    qry="select * from products"
    res=selectall(qry)
    return render_template("MANUFACTURE/MANAGE PRODUCTS.html",val=res)







@app.route('/manufacturehome',methods=['post','get'])
@login_required
def manufacturehome():
    return render_template("MANUFACTURE/MANUFACTURE  HOME.html")


@app.route('/viewrequestfromagency',methods=['post','get'])
@login_required
def viewrequestfromagency():
    qry="SELECT `agency`.*,`productrequest`.*,`products`.`name`,image FROM `agency` JOIN `productrequest` ON `agency`.`lid`=`productrequest`.`lid` JOIN `products` ON `productrequest`.`pid`=`products`.`pid`"
    res=selectall(qry)
    return render_template("MANUFACTURE/VIEW REQUEST FROM AGENCY.html",val=res)




@app.route('/acceptrequest',methods=['post','get'])
@login_required
def acceptrequest():
    id=request.args.get('id')
    qry="update productrequest set status='accept' where reqid=%s"
    iud(qry,id)
    return '''<script>alert("accepted..");window.location='/viewrequestfromagency#about'</script>'''


@app.route('/rejectrequest',methods=['post','get'])
@login_required
def rejectrequest():
    id = request.args.get('id')
    qry = "update productrequest set status='reject' where reqid=%s"
    iud(qry, id)
    return '''<script>alert("rejected..");window.location='/viewrequestfromagency#about'</script>'''


########################shop#####################


@app.route('/shophome',methods=['post','get'])
@login_required
def shophome():
    return render_template("SHOP/SHOP HOME.html")

@app.route('/viewagencybysearch',methods=['post','get'])
@login_required
def viewagencybysearch():
    qry = "select * from agency"
    res=selectall(qry)
    return render_template("SHOP/VIEWAGENCYBYSEARCHANDREQUEST.html",val=res)


@app.route('/search',methods=['post','get'])
@login_required
def search():
    agency=request.form['select']
    qry1="SELECT `productrequest`.*,`products`.* FROM `productrequest` JOIN `products` ON `productrequest`.`pid`=`products`.`pid` WHERE `productrequest`.status='accept' AND `productrequest`.`lid`=%s"
    res1=selectall2(qry1,agency)
    qry = "select * from agency"
    res = selectall(qry)

    return render_template("SHOP/VIEWAGENCYBYSEARCHANDREQUEST.html",val1=res1,val=res)



@app.route('/verifyprdct')
def verifyprdct():
    id=request.args.get('id')
    qry="SELECT `image` FROM `products` WHERE `pid`=%s"
    res=selectone(qry,id)
    fs=res['image']
    key="myencryptionkey"
    with open(os.path.join('static/uploads',fs), "rb") as imageFile:
        stri = base64.b64encode(imageFile.read()).decode('utf-8')
        dec2 = decrypt(stri, key).decode('utf-8')
        fh1 = open("static/decrpt/"+fs, "wb")
        fh1.write(base64.b64decode(dec2))
        fh1.close()
    v="verification failed"
    if validate_sign(os.path.join('static/uploads',fs),id):
        v = "verified"
    return render_template("SHOP/verification.html",v=v,fn=fs)




@app.route('/reqquantity_shop',methods=['post','get'])
@login_required
def reqquantity_shop():
    id=request.args.get('iid')
    session['prodid']=id

    return render_template("SHOP/requestquantity.html")



@app.route('/reqquantity_shop1',methods=['post','get'])
@login_required
def reqquantity_shop1():
    qty=request.form['textfield']
    qry="INSERT INTO `requestproduct_shop` values(NULL,%s,CURDATE(),'pending',%s,%s)"
    val=(session['prodid'],qty,session['lid'])
    iud(qry, val)
    return '''<script>alert("request sended..");window.location='/shophome#about'</script>'''



@app.route('/requeststatus_shop',methods=['post','get'])
@login_required
def requeststatus_shop():
    qry="SELECT `agency`.`fname`,`lname` ,`requestproduct_shop`.*,`products`.`name`,`products`.image,requestproduct_shop.date as dt FROM `requestproduct_shop` JOIN `products` ON `requestproduct_shop`.`pid`=`products`.`pid` JOIN `productrequest` ON `productrequest`.`pid`=`products`.`pid` JOIN `agency` ON `agency`.`lid`=`productrequest`.`lid` WHERE `productrequest`.`status`='accept' AND `requestproduct_shop` .`lid`=%s"
    res=selectall2(qry,session['lid'])
    return render_template("SHOP/REQUEST STATUS _shop.html",val=res)




app.run(debug=True)
















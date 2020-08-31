from flask import Flask, render_template, request, url_for, redirect, flash, session
# from flask_mysqldb import MySQL
from flaskext.mysql import MySQL
from flask_assets import Environment, Bundle
import json 
import bcrypt

app = Flask(__name__)

# Mysql connections
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
app.config['MYSQL_DATABASE_DB'] = 'proyecto'
mysql = MySQL(app)
mysql.init_app(app)

# settings
app.secret_key = 'mysecretkey'

#semilla para encriptamiento
semilla = bcrypt.gensalt()

@app.route('/')
def Index():
    return render_template('index.html')

@app.route('/register')
def Register():
    if 'nombre' in session:
        return render_template('admin.html')
    else:
        return render_template('register.html')

@app.route('/registeremp', methods=['GET', 'POST'])
def Registeremp():
    if request.method=="GET":
        if 'nombreemp' in session:
            return redirect(url_for('Adminemp'))
        else:
            return render_template('loginempleado.html')
    else:
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("""SELECT m.nombre, s.codigo, s.nombre, s.direccion
                        FROM sede s
                        INNER JOIN municipio m ON m.codigo=s.codigo_municipio
                        ORDER BY m.nombre;""")
        data=cur.fetchall()
        cur.execute("""SELECT id, nombre
                        FROM tipo_empleado
                        """)
        data2=cur.fetchall()
        return render_template('registeremp.html', sedes=data, tipos=data2)


@app.route('/registrar', methods=["GET", "POST"])
#fUNCION PARA registar usuarios
def Registrar():
    if request.method=="GET":
        if 'nombre' in session:
            return render_template('admin.html')
        else:
            return render_template('login.html')
    else:
        #Obtiene los datos del formulario
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        barrio = request.form['barrio']
        sexo = request.form.getlist('exampleRadios')
        municipio = request.form.getlist('municipio')
        password_encode = password.encode("utf-8")
        password_encriptado = bcrypt.hashpw(password_encode, semilla)
        con = mysql.connect()
        cur = con.cursor()
        
        cur.execute("""INSERT INTO usuario (nombre, email, telefono, direccion, barrio, sexo, codigo_municipio) VALUES 
							(%s, %s, %s, %s, %s, %s, %s);""", (nombre, email, telefono, direccion, barrio, sexo, municipio))
        cur.execute("""INSERT INTO datos_log VALUES (%s,%s)""", (email, password_encriptado))
 
        con.commit()

        return redirect(url_for('Login'))

@app.route('/registraremp', methods=["GET", "POST"])
#fUNCION PARA registar empleados
def Registraremp():
    if request.method=="GET":
        if 'nombre' in session:
            return render_template('empleado.html')
        else:
            return render_template('loginempleado.html')
    else:
        #Obtiene los datos del formulario
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        sexo = request.form.getlist('exampleRadios')
        codigo_sede = request.form.getlist('sedes')
        codigo_empleado = request.form.getlist('empleadotipo')
        password_encode = password.encode("utf-8")
        password_encriptado = bcrypt.hashpw(password_encode, semilla)
        con = mysql.connect()
        cur = con.cursor()
        
        cur.execute("""INSERT INTO empleado (nombre, email, sexo, codigo_sede, id_tipoempleado) 
                VALUES (%s, %s, %s, %s, %s)""", (nombre, email, sexo, codigo_sede, codigo_empleado))
        cur.execute("""INSERT INTO datos_log VALUES (%s,%s)""", (email, password_encriptado))
 
        con.commit()

        return redirect(url_for('Login2emp'))

@app.route('/login')
def Login():
    if 'nombre' in session:
        return redirect(url_for('Admin'))
    else:
        return render_template('login.html')


@app.route('/loginempleado')
def Loginempleado():
    if 'nombreemp' in session:
        return redirect(url_for('Adminemp'))
    else:
        
        return render_template('loginempleado.html')

@app.route('/login2emp', methods=["GET", "POST"])
def Login2emp():
    if request.method=="GET":
        if 'nombreemp' in session:
            return redirect(url_for('Adminemp'))
        else:
            return render_template('loginempleado.html')
    else:
        if 'nombreemp' in session:
            return redirect(url_for('Adminemp'))
        else:
            email = request.form['email']
            password = request.form['password']
            password_encode = password.encode("utf-8")
            con=mysql.connect()
            cur = con.cursor()
            cur.execute("""
                        SELECT d.email, d.password, u.nombre, u.id
                        FROM datos_log d
                        INNER JOIN empleado u ON u.email = d.email
                        WHERE d.email = %s;
                            """, [email])

            usuario = cur.fetchone()

            cur.close()

            if (usuario != None):
                password_encriptado_encode = usuario[1].encode()

                if(bcrypt.checkpw(password_encode, password_encriptado_encode)):
                    session['nombreemp'] = usuario [2]
                    session['correoemp'] = email
                    session['iduseremp'] = usuario [3]

                    return redirect(url_for('Adminemp'))
                else:
                    flash("El password no es correcto", "alert-warning")

                    return render_template('loginemp.html')
            else:
                flash("El email no existe", "alert-warning")
                return render_template('loginempleado.html')

    
@app.route('/login2', methods=["GET", "POST"])
def Login2():
    if request.method=="GET":
        if 'nombre' in session:
            return render_template('admin.html')
        else:
            return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        password_encode = password.encode("utf-8")
        con=mysql.connect()
        cur = con.cursor()
        cur.execute("""
                    SELECT d.email, d.password, u.nombre, u.id
                    FROM datos_log d
                    INNER JOIN usuario u ON u.email = d.email
                    WHERE d.email = %s;
                        """, [email])

        usuario = cur.fetchone()

        cur.close()

        if (usuario != None):
            password_encriptado_encode = usuario[1].encode()

            if(bcrypt.checkpw(password_encode, password_encriptado_encode)):
                session['nombre'] = usuario [2]
                session['correo'] = email
                session['iduser'] = usuario [3]

                return redirect(url_for('Admin'))
            else:
                flash("El password no es correcto", "alert-warning")

                return render_template('login.html')
        else:
            flash("El email no existe", "alert-warning")
            return render_template('login.html')

@app.route('/crearcarrito')
def Crearcarrito():
    if 'nombre' in session:
        if 'order' in session:
            return redirect(url_for('Carrito'))
        else:
            con=mysql.connect()
            cur = con.cursor()
            cur.execute("""SELECT codigo, nombre, direccion
                        FROM sede
                        WHERE codigo_municipio IN 
                        (SELECT codigo_municipio FROM usuario WHERE id=%s);""",(session['iduser']))
            data2 = cur.fetchall()
            return render_template('crearcarrito.html', sedes=data2)
    else:
        return render_template('login.html')


@app.route('/carrito')
def Carrito():
    if 'nombre' in session:
        if 'order' in session:
            con=mysql.connect()
            cur = con.cursor()
            cur.execute("""SELECT (SELECT SUM(d.cantidad*p.precio) 
            FROM detalle_pedido d
            INNER JOIN producto p ON p.codigo = d.codigo_producto
            WHERE d.codigo_pedido = %s),
            p.id, ep.nombre, s.nombre, s.direccion, u.id, u.nombre, u.telefono, u.direccion, u.barrio, u.email,
            sp.f_creacion, sp.f_solicitacion, sp.f_despacho, sp.f_finalizacion
            FROM pedido p
            INNER JOIN sede s ON s.codigo = p.codigo_sede
            INNER JOIN estado_pedido ep ON ep.id = p.id_estado
            INNER JOIN usuario u ON u.id = p.id_usuario
            INNER JOIN seguimiento_pedido sp ON sp.id_pedido = %s
            WHERE p.id=%s;""",(session['order'], session['order'], session['order']))

            orderdata = cur.fetchone()

            if orderdata[0]:
                cur.execute("""SELECT p.nombre, p.precio, d.cantidad, d.id, p.codigo
                                FROM detalle_pedido d
                                INNER JOIN producto p ON p.codigo = d.codigo_producto
                                WHERE d.codigo_pedido = %s;""",(session['order']))
                orderdetails = cur.fetchall()
                return render_template('carrito.html', cabecera = orderdata, detalles=orderdetails)
            else:
                return render_template('carrito.html', cabecera = orderdata, detalles=0)
        else:
            return redirect(url_for('Crearcarrito'))


    else:
        return render_template('login.html')


@app.route('/solicitarpedido', methods=['GET', 'POST'])
def solicitarpedido():
    if 'nombre' in session:
        if 'order' in session:
             if request.method=='POST':
                idpedido = request.form['idpedido']
                con=mysql.connect()
                cur = con.cursor()
                iduser = session['iduser']
                cur.execute("""UPDATE pedido SET id_estado = 1
                                WHERE id=%s""", (idpedido))
                con.commit()
                session.pop('order',None)
                
                return redirect(url_for('Admin'))           
            
        else: 
            return redirect(url_for('Carrito'))
    else:
        return render_template('login.html')


@app.route('/createorder', methods=['GET', 'POST'])
def Createorder():
    if 'nombre' in session:
        if 'order' in session:
            return redirect(url_for('Carrito'))
        else: 
            if request.method=='POST':
                sede = request.form.getlist('sedes')
                con=mysql.connect()
                cur = con.cursor()
                iduser = session['iduser']
                cur.execute('INSERT INTO pedido (id_estado, codigo_sede, id_usuario) VALUES (4, %s, %s)', (sede, iduser))
                cur.execute('SELECT MAX(id) FROM pedido WHERE id_usuario = %s',(iduser))
                order = cur.fetchone()
                session['order'] = order[0]
                cur.execute("""INSERT INTO seguimiento_pedido (id_pedido, f_creacion)
                                VALUES (%s, NOW())""",(session['order']))
                con.commit()
                
                return redirect(url_for('Carrito'))
    else:
        return render_template('login.html')

@app.route('/gestionarpedidoemp/<id>')
def Gestionarpedidoemp(id):
    if 'nombreemp' in session:
        con=mysql.connect()
        cur = con.cursor()
        cur.execute("""SELECT (SELECT SUM(d.cantidad*p.precio) 
        FROM detalle_pedido d
        INNER JOIN producto p ON p.codigo = d.codigo_producto
        WHERE d.codigo_pedido = %s),
        p.id, ep.nombre, s.nombre, s.direccion, u.id, u.nombre, u.telefono, u.direccion, u.barrio, u.email,
        sp.f_creacion, sp.f_solicitacion, sp.f_despacho, sp.f_finalizacion
        FROM pedido p
        INNER JOIN sede s ON s.codigo = p.codigo_sede
        INNER JOIN estado_pedido ep ON ep.id = p.id_estado
        INNER JOIN usuario u ON u.id = p.id_usuario
        INNER JOIN seguimiento_pedido sp ON sp.id_pedido = %s
        WHERE p.id=%s;""",(id, id, id))
        orderdata = cur.fetchone()     
        cur.execute("""SELECT p.nombre, p.precio, d.cantidad, d.id, p.codigo
                            FROM detalle_pedido d
                            INNER JOIN producto p ON p.codigo = d.codigo_producto
                            WHERE d.codigo_pedido = %s;""",(id))
        orderdetails = cur.fetchall()
        cur.execute("""SELECT *
                        FROM estado_pedido
                        WHERE id in (2,3)""")
        est = cur.fetchall()
        cur.execute("""SELECT id_estado
                        FROM pedido
                        WHERE id = %s""",(id))
        actual = cur.fetchone()
        return render_template('gestionarpedido.html', cabecera = orderdata, detalles=orderdetails, estados = est, actualstate=actual[0])  

    else:
        return render_template('loginempleado.html')

@app.route('/despacharpedido', methods=['GET', 'POST'])
def Despacharpedido():
    if 'nombreemp' in session:
        if request.method == 'POST':
            idpedido = request.form['idpedido']
            idestado = request.form.getlist('states')
            con=mysql.connect()
            cur=con.cursor()
            cur.execute("""UPDATE pedido SET id_estado=%s
                            WHERE id = %s""",(idestado, idpedido))
            con.commit()
            return redirect(url_for('Adminemp'))

    else:
        return render_template('loginempleado.html')

@app.route('/finalizarpedido', methods=['GET', 'POST'])
def Finalizarpedido():
    if 'nombreemp' in session:
        if request.method == 'POST':
            idpedido = request.form['idpedido']
            con=mysql.connect()
            cur=con.cursor()
            cur.execute("""UPDATE pedido SET id_estado=3
                            WHERE id = %s""",(idpedido))
            con.commit()
            return redirect(url_for('Adminemp'))

    else:
        return render_template('loginempleado.html')

@app.route('/gestionarpedidouser/<id>')
def Gestionarpedidouser(id):
    if 'nombre' in session:
        con=mysql.connect()
        cur = con.cursor()
        cur.execute("""SELECT (SELECT SUM(d.cantidad*p.precio) 
        FROM detalle_pedido d
        INNER JOIN producto p ON p.codigo = d.codigo_producto
        WHERE d.codigo_pedido = %s),
        p.id, ep.nombre, s.nombre, s.direccion, u.id, u.nombre, u.telefono, u.direccion, u.barrio, u.email,
        sp.f_creacion, sp.f_solicitacion, sp.f_despacho, sp.f_finalizacion
        FROM pedido p
        INNER JOIN sede s ON s.codigo = p.codigo_sede
        INNER JOIN estado_pedido ep ON ep.id = p.id_estado
        INNER JOIN usuario u ON u.id = p.id_usuario
        INNER JOIN seguimiento_pedido sp ON sp.id_pedido = %s
        WHERE p.id=%s;""",(id, id, id))
        orderdata = cur.fetchone()     
        cur.execute("""SELECT p.nombre, p.precio, d.cantidad, d.id, p.codigo
                            FROM detalle_pedido d
                            INNER JOIN producto p ON p.codigo = d.codigo_producto
                            WHERE d.codigo_pedido = %s;""",(id))
        orderdetails = cur.fetchall()
        cur.execute("""SELECT *
                        FROM estado_pedido
                        WHERE id in (2,3)""")
        est = cur.fetchall()
        return render_template('gestionarpedidouser.html', cabecera = orderdata, detalles=orderdetails, estados = est)  

    else:
        return render_template('login.html')

@app.route('/salir')
def Salir():
    con=mysql.connect()
    cur = con.cursor()
    if 'order' in session:
        cur.execute("""SELECT id_estado
                        FROM pedido
                        WHERE id = %s
                        """, (session['order']))
        state=cur.fetchone()

        if state[0] == 4:
            cur.execute("""DELETE FROM seguimiento_pedido WHERE id_pedido=%s""",
                    (session['order']))        
            cur.execute("""DELETE FROM detalle_pedido WHERE codigo_pedido=%s""",
                            (session['order']))
            cur.execute("""DELETE FROM pedido WHERE id=%s""",
                    (session['order']))

        con.commit()
    session.clear()

    return redirect(url_for('Index'))

@app.route('/admin')
def Admin():
    if 'nombre' in session:
        con=mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT * FROM contacts')
        data = cur.fetchall()
        cur.execute("""SELECT codigo, nombre, direccion
                    FROM sede
                    WHERE codigo_municipio IN 
                    (SELECT codigo_municipio FROM usuario WHERE id=%s);""",(session['iduser']))
        data2 = cur.fetchall()
        return render_template('admin.html', contacts = data, sedes=data2)
    else:
        return render_template('login.html')

@app.route('/adminemp')
def Adminemp():
    if 'nombreemp' in session:
        con=mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT * FROM contacts')
        data = cur.fetchall()
        cur.execute('SELECT id_tipoempleado FROM empleado WHERE id = %s',(session['iduseremp']))
        data2 = cur.fetchone()
        return render_template('adminemp.html', contacts = data, tipo = data2)
    else:
        return render_template('loginempleado.html')
    
@app.route('/empleado')
def Empleado():
    if 'nombreemp' in session:
        con=mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT * FROM contacts')
        data = cur.fetchall()
        cur.execute("""SELECT (SELECT SUM(d.cantidad*p.precio) 
                    FROM detalle_pedido d
                    INNER JOIN producto p ON p.codigo = d.codigo_producto
                    WHERE d.codigo_pedido = p.id),
                    p.id, ep.nombre, s.nombre, s.direccion, u.id, u.nombre, u.telefono, u.direccion, u.barrio, u.email,
                    sp.f_creacion, sp.f_solicitacion, sp.f_despacho, sp.f_finalizacion
                    FROM pedido p
                    INNER JOIN sede s ON s.codigo = p.codigo_sede
                    INNER JOIN estado_pedido ep ON ep.id = p.id_estado
                    INNER JOIN usuario u ON u.id = p.id_usuario
                    INNER JOIN seguimiento_pedido sp ON sp.id_pedido = p.id
                    WHERE p.id_estado = 1
                    ;""")
        data2 = cur.fetchall()
        return render_template('empleado.html', pedidos = data2)
    else:
        return render_template('loginempleado.html')

@app.route('/empleadofinalizar')
def Empleadofinalizar():
    if 'nombreemp' in session:
        con=mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT * FROM contacts')
        data = cur.fetchall()
        cur.execute("""SELECT (SELECT SUM(d.cantidad*p.precio) 
                    FROM detalle_pedido d
                    INNER JOIN producto p ON p.codigo = d.codigo_producto
                    WHERE d.codigo_pedido = p.id),
                    p.id, ep.nombre, s.nombre, s.direccion, u.id, u.nombre, u.telefono, u.direccion, u.barrio, u.email,
                    sp.f_creacion, sp.f_solicitacion, sp.f_despacho, sp.f_finalizacion
                    FROM pedido p
                    INNER JOIN sede s ON s.codigo = p.codigo_sede
                    INNER JOIN estado_pedido ep ON ep.id = p.id_estado
                    INNER JOIN usuario u ON u.id = p.id_usuario
                    INNER JOIN seguimiento_pedido sp ON sp.id_pedido = p.id
                    WHERE p.id_estado = 2
                    ;""")
        data2 = cur.fetchall()
        return render_template('empleadofinalizar.html', pedidos = data2)
    else:
        return render_template('loginempleado.html')


@app.route('/usuario')
def Usuario():
    if 'nombre' in session:
        con=mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT * FROM contacts')
        data = cur.fetchall()
        cur.execute("""SELECT (SELECT SUM(d.cantidad*p.precio) 
                    FROM detalle_pedido d
                    INNER JOIN producto p ON p.codigo = d.codigo_producto
                    WHERE d.codigo_pedido = p.id),
                    p.id, ep.nombre, s.nombre, s.direccion, u.id, u.nombre, u.telefono, u.direccion, u.barrio, u.email,
                    sp.f_creacion, sp.f_solicitacion, sp.f_despacho, sp.f_finalizacion
                    FROM pedido p
                    INNER JOIN sede s ON s.codigo = p.codigo_sede
                    INNER JOIN estado_pedido ep ON ep.id = p.id_estado
                    INNER JOIN usuario u ON u.id = p.id_usuario
                    INNER JOIN seguimiento_pedido sp ON sp.id_pedido = p.id
                    ;""")
        data2 = cur.fetchall()
        return render_template('usuario.html', pedidos = data2)
    else:
        return render_template('login.html')

@app.route('/frutas')
def Frutas():
    con=mysql.connect()
    cur = con.cursor()
    cur.execute("""SELECT p.codigo, p.nombre, p.precio, p.descripcion, p.urlimage
                FROM producto p
                INNER JOIN categoria_producto c ON c.id = p.id_categoria
                INNER JOIN sede s ON s.codigo = p.codigo_sede
                WHERE c.id = 1
                ORDER BY p.destacado desc, p.nombre""")
    data = cur.fetchall()
    return render_template('frutas.html', frutas = data)

@app.route('/verduras')
def Verduras():
    con=mysql.connect()
    cur = con.cursor()
    cur.execute("""SELECT p.codigo, p.nombre, p.precio, p.descripcion
                FROM producto p
                INNER JOIN categoria_producto c ON c.id = p.id_categoria
                INNER JOIN sede s ON s.codigo = p.codigo_sede
                WHERE c.id = 2
                ORDER BY p.nombre""")
    data = cur.fetchall()
    return render_template('verduras.html', frutas = data)

@app.route('/addproduct/<id>')
def getaddprod(id):
    if 'nombre' in session:
        if 'order' in session:
            con=mysql.connect()
            cur = con.cursor()
            cur.execute("""SELECT * FROM detalle_pedido 
                            WHERE codigo_producto = %s AND codigo_pedido = %s
                            """,(id, session['order']))
            hay=cur.fetchone()

            if hay:
                con=mysql.connect()
                cur = con.cursor()
                cur.execute("""SELECT codigo, nombre, precio, descripcion, urlimage
                                FROM producto 
                                WHERE codigo = %s;""",(id))
                data = cur.fetchall()
                return render_template('carroproductoedit.html', fruta = data[0])
            else:
                con=mysql.connect()
                cur = con.cursor()
                cur.execute("""SELECT codigo, nombre, precio, descripcion, urlimage
                                FROM producto 
                                WHERE codigo = %s;""",(id))
                data = cur.fetchall()
                return render_template('carroproducto.html', fruta = data[0])
        else:
            return redirect(url_for('Crearcarrito'))

    else:
        return render_template('login.html')


@app.route('/insertprod/<id>', methods=['GET', 'POST'])
def getinsertproduct(id):
    if 'nombre' in session:
        if 'order' in session:
            if request.method=='POST':
                cantidad = request.form['cantidad']
                con=mysql.connect()
                cur = con.cursor()
                cur.execute("""INSERT INTO detalle_pedido (cantidad, codigo_producto, codigo_pedido) 
                            VALUES (%s,%s,%s)""",(cantidad,id,session['order']))  
                con.commit()
                return redirect(url_for('Carrito'))  
            
        else: 
            return redirect(url_for('Carrito'))
           
    else:
        return render_template('login.html')

@app.route('/updateprod/<id>', methods=['GET', 'POST'])
def getupdateproduct(id):
    if 'nombre' in session:
        if request.method=='POST':
            cantidad = request.form['cantidad']
            con=mysql.connect()
            cur = con.cursor()
            cur.execute("""UPDATE detalle_pedido SET cantidad = %s
                            WHERE codigo_producto = %s AND codigo_pedido = %s""",
                            (cantidad,id,session['order']))  
            con.commit()
            return redirect(url_for('Carrito'))  
           
    else:
        return render_template('login.html')

@app.route('/add_contact', methods=['POST'])
def add_contact():
    if 'nombre' in session:
        if request.method=='POST':
            nombre = request.form['nombre']
            telefono = request.form['telefono']
            email = request.form['email']
            con=mysql.connect()
            cur = con.cursor()
            cur.execute('INSERT INTO contacts (nombre, telefono, email) VALUES (%s,%s,%s)',(nombre,
            telefono,email))
            con.commit()
            flash('Contact Added Succesfully')
            return redirect(url_for('Admin'))
    else:
        return render_template('login.html')


@app.route('/edit/<id>')
def get_contact(id):
    if 'nombre' in session:
        con=mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT * FROM contacts WHERE id = %s',[id])
        data = cur.fetchall()
        return render_template('editcontact.html', contact = data[0])
    else:
        return render_template('login.html')

@app.route('/update/<id>', methods = ['POST'])
def update_contact(id):
    if 'nombre' in session:
        if request.method == 'POST':
            nombre = request.form['nombre']
            telefono = request.form['telefono']
            email = request.form['email']
            con=mysql.connect()
            cur = con.cursor()
            cur.execute("""
            UPDATE contacts
            SET nombre = %s,
                telefono = %s,
                email = %s
            WHERE id = %s
            """, (nombre, telefono, email, id))
            con.commit()
            flash('Contact eddited succesfully')
            return redirect(url_for('Admin'))
    else: 
        return render_template('login.html')


@app.route('/delete/<id>')
def delete(id):
    if 'nombre' in session:
        if request.method == 'GET':
            con=mysql.connect()
            cur = con.cursor()
            cur.execute('DELETE FROM contacts WHERE id = %s',[id])
            con.commit()
            flash('Contact Removed Succesfully')
            cur.execute('SELECT * FROM contacts')
            return redirect(url_for('Admin'))
    else: 
        return render_template('login.html')

if __name__ == '__main__':
    app.run(port = 3000, debug = True)



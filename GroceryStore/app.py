# ===========================================================================================
# ======================================== Imports ==========================================
# ===========================================================================================

from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy #database used in this application is sqlite db and connected via SQLAlchemy

# ===========================================================================================
# =========================== Initialization and Configurations =============================
# ===========================================================================================

#initilises the flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gs.db'
app.config['SECRET_KEY'] = 'as89hsHDWIHU7q7q88wdWHknk88HDwkdbw'
db = SQLAlchemy(app)

# ===========================================================================================
# ======================================== Models ===========================================
# ===========================================================================================

'''
User model which handes all database actions reated to user
'''
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self): #returns user's id and usernmae
        return f"User('{self.id}','{self.username}')"

'''
Category model which is used to handle all database related things related to the categories of products
'''
class Category(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    category_name = db.Column(db.String(20), unique=True, nullable=False)
    items = db.relationship('Product', backref='section')   #its the relationship between categories and products

    def __repr__(self): #it returns category id and its name
        return f"Category('{self.id}','{self.category_name}')"

'''
Product model which is used to handle all database operations related to the products
'''
class Product(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    product_name = db.Column(db.String(20), unique=True, nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    m_and_e_date = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    quantity = db.Column(db.Float(), nullable=False)
    cat = db.Column(db.Integer(), db.ForeignKey('category.id')) #connects the category's id table as its foreign key
    # relation_with_user = db.relationship('User', backref='rel_user')

    def __repr__(self): #it returns all the products attributes like id, name, unit, etc.
        return f"Product('{self.id}','{self.product_name}','{self.unit}','{self.m_and_e_date}', '{self.price}','{self.quantity}','{self.cat}')"

# ===========================================================================================
# ===================================== Global lists ========================================
# ===========================================================================================

#global lists used to store users in application
userG = []
#global list of products in cart
carted_products = []
#global list of product quantities
prod_quantity=[]

# ===========================================================================================
# ======================================== Routes ===========================================
# ===========================================================================================

'''
It is the home route. Login page is available for users login
'''
@app.route('/', methods=['GET', 'POST'])    #this route handles get and post requests
def login():
    error=None  #this message is changed according to the conditions and displayed on login page
    if request.method == "POST":    #for post requests
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        #necessary conditions for login vaidation
        if user is None:
            return render_template('login.html', error='Invalid username or password.')
        if password == user.password:
            categories = Category.query.all()
            productss = Product.query.all()
            products = list(reversed(productss))
            userG.append(user)  #its a global list used for other routes
            # userG.append(user)
            units = ['  Rs/Kg', '  Rs/Liter', '  Rs/gram', '  Rs/dozen']
            # print(type(products))
            return render_template('store.html', user=user, categories=categories, products=products, units=units)
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    #for get requests
    return render_template('login.html', error=error)

'''
This route handles the go to store button requests
'''
@app.route('/go_to_store', methods=['GET', 'POST'])
def go_to_store():
    if userG:   #its used to capture the current users name
        userr=userG[-1].username
    usern=userr
    # userG.append(usern)
    # print('----------------------------', usern)    
    user = User.query.filter_by(username=usern).first()
    # user = usern
    # passwordG= passwordG.pop()
    categories = Category.query.all()
    productss = Product.query.all()
    products = list(reversed(productss))
    units = ['  Rs/Kg', '  Rs/Liter', '  Rs/gram', '  Rs/dozen']
    # print(type(products))
    #it renders the store page with all the required lists above
    return render_template('store.html', user=user, categories=categories, products=products, units=units)

'''
Register route is used to register new users to the application's database
'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    error=None
    if request.method == 'POST':
        #storing username, passwd in local variables
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match.')

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already taken.')
        else:
            new_user = User(username=username, password=password)
            
            #adding and commiting of new user is done by following lines ofcode
            db.session.add(new_user)
            db.session.commit()
            
            return redirect(url_for('login'))   #it redirects to the function defined for any perticular route by using that functions url name
    return render_template('register.html', error=error)

'''
It is the route for admin login. Only specific users can login as admin
'''
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error=None
    admin='ad'
    password='ad'
    if request.method == 'POST':
        #method below checks it admin crediantials and render template accordingly
        if admin != request.form.get('username') or password != request.form.get('password'):
            error='Invalid cerdintials'
            return render_template('admin_login.html', error=error)
        else:
            return redirect(url_for('dashboard'))
    return render_template('admin_login.html', error=error)

'''
Dashboard route is used by admins to CRUD and perform other operations on categories and products
'''
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    categories = Category.query.all()   #queries all categories from db
    return render_template('dashboard.html', categories=categories)

'''
Adds categories of products to the database
'''
@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method=="POST":  
        # print('hi')
        category_name = request.form.get('add_category')
        # print(category_name)
        if not Category.query.filter_by(category_name=category_name).first():   #if category isn't available adds it and if its already present do nothing
            cat = Category(category_name=category_name)
            db.session.add(cat)
            db.session.commit()
        else:
            pass
        return redirect(url_for('dashboard'))
    if request.method == 'GET': 
        # print('hi')
        return render_template('add_category.html')

'''
Viewing of products is done via this route
'''
@app.route('/view_products/<int:id>', methods=['GET', 'POST'])  #product id is taken from page
def view_products(id):
    products = Product.query.all()
    return render_template('view_product.html',products=products,id=id)

'''
It creates product by taking product id as parameter
'''
@app.route('/create_product/<int:id>', methods=['GET', 'POST'])
def create_product(id):
    if request.method == 'POST':
        unit = request.form.get('unit')
        #debuggers
        # print('======================================================')
        # print(unit)
        # print('======================================================')
        
        #captures all attributes of product
        cat=id  #id of category
        product_name = request.form.get('product_name')
        product_price = int(request.form.get('product_price'))
        m_and_e_date = request.form.get('m_and_e_date')
        product_quantity = float(request.form.get('product_quantity'))
        
        #saving product to db
        prod = Product(product_name=product_name, unit = unit, m_and_e_date=m_and_e_date, price=product_price, quantity=product_quantity, cat=cat)
        db.session.add(prod)
        db.session.commit()
        
        products = Product.query.all()
        # return redirect(url_for('all_products'))
        return render_template('view_product.html', products=products, id=cat)
        # return redirect(url_for('view_product'))
    
    #for get requset
    units={0:'Rs/Kg', 1:'Rs/Liter', 2:'Rs/gram', 3:'Rs/dozen'}  #this dictionary maps int unit in db to its string form
    return render_template('create_product.html',id=id, units=units)

'''
It confirms deletion of product by taking products id and its respective category id
'''
@app.route('/delete_confirmation/<int:id>/<int:cat>', methods=['GET', 'POST'])
def delete_confirmation(id, cat):
    return render_template('delete_confirmation.html', id=id, cat=cat)  #returns confirmation page

'''
It confirms deletion of category/section by taking its id
'''
@app.route('/delete_category_confirmation/<int:id>', methods=['GET', 'POST'])
def delete_category_confirmation(id):
    return render_template('delete_category_confirmation.html', id=id)

'''
Deletes the product by taking its id and its category id
'''
@app.route('/delete_product/<int:id>/<int:cat>', methods=['GET', 'POST'])
def delete_product(id, cat):
    # print("--------------------------------------------",id)
    prod = Product.query.get(id)
    # print("--------------------------------------------",prod)
    if prod is None:    #aborts operation if no product found
        abort(404)
    db.session.delete(prod)
    db.session.commit()
    #debuggers
    # products = Product.query.all()
    # print('...........deleted.......')
    # return render_template('view_product.html', products=products, id=cat)

    return redirect(url_for('view_products', id=cat))

'''
Deletes category by taking its id
'''
@app.route('/delete_category/<int:id>', methods=['GET', 'POST'])
def delete_category(id):
    category = Category.query.get(id)
    if category is None:
        abort(404)
        
    #captures products related to the category which is gonna be deleted and deletes them
    products = Product.query.filter_by(cat=id).all()
    for product in products:
        db.session.delete(product)
    db.session.delete(category)
    db.session.commit()
    
    return redirect(url_for('dashboard'))

'''
Updates the product taking its id and category's id
'''
@app.route('/update_product/<int:id>/<int:cat>', methods=['GET', 'POST'])
def update_product(id, cat):
    if request.method=="POST":
        # return render_template('test.html')
        #captures data from page
        product = Product.query.get_or_404(id)
        product_name = request.form.get('product_name')
        unit = request.form.get('unit')
        m_and_e_date = request.form.get('m_and_e_date')
        product_price = request.form.get('product_price')
        product_quantity = request.form.get('product_quantity')
        
        #updates the product with the new values
        product.product_name = product_name
        product.unit = unit
        product.m_and_e_date = m_and_e_date
        product.price = product_price
        product.quantity = product_quantity
        
        db.session.commit()
        return redirect(url_for('view_products', id=cat))
    #get request
    product = Product.query.filter_by(id=id).first()

    #debuggers
    # print('======================================================')
    # print(product.product_name)
    # print('======================================================')
    
    units = {0: 'Rs/Kg', 1: 'Rs/Liter', 2: 'Rs/gram', 3: 'Rs/dozen'}
    return render_template('update_product.html', product=product, units=units)

'''
Updates category of products by using its id
'''
@app.route('/update_category/<int:id>', methods=['GET', 'POST'])
def update_category(id):
    if request.method=="POST":
        #captures category and updates it
        # return render_template('test.html')
        category = Category.query.get_or_404(id)
        category_name = request.form.get('category_name')
        # Update the product with the new values
        category.category_name = category_name
        db.session.commit()
        return redirect(url_for('dashboard'))
    #get request
    category = Category.query.filter_by(id=id).first()
    return render_template('update_category.html', category=category)

'''
Buy products using their id
'''
@app.route('/buy_product/<int:id>', methods=['GET', 'POST'])
def buy_product(id):
    error=None
    product = Product.query.filter_by(id=id).first()
    units = {0: 'Kg', 1: 'Liter', 2: 'gram', 3: 'dozen'}
    if request.method=="POST":
        quantity = float(request.form.get('product_quantity'))    #converts product quantity to integer from string
        total=quantity*product.price    #calculates the total price to be paid for byued product/s
        # print('-----------------------',quantity)
        if quantity > product.quantity: #if user ask for more quantity than available show following error
            error = f"Your need is greater than this product's available quantity. Only {product.quantity} unit/s remaining..."
            return render_template('buy_product.html', product=product, units=units, error=error)
        else:   #for successful input
            return render_template('buy.html', product=product, units=units, quantity=quantity, total=total)
    # print(type(product.section))
    return render_template('buy_product.html', product=product, units=units, error=error)

'''
Final step in buying product/s and updating the inventry
'''
@app.route('/buy/<int:id>/<float:qt>', methods=['POST'])
def buy(id, qt):    #has id of product and quantity bought
    if request.method=="POST":
        #updating quantity of bought product
        product = Product.query.get_or_404(id)
        product.quantity = abs(product.quantity-qt)
        db.session.commit()
        return render_template('test.html' )    #demo template for successful transaction

'''
It adds the product to the cart
'''
@app.route('/add_to_cart/<int:id>', methods=['GET', 'POST'])
def add_to_cart(id):
    units = {0: 'Kg', 1: 'Liter', 2: 'gram', 3: 'dozen'}
    
    if request.method=="POST":
        product = Product.query.filter_by(id=id).first()
        carted_products.append(product) #appends the product to carted_products list
        # print('---------------------',carted_products)
        return redirect(url_for('go_to_store'))
    
    
    if request.method=="GET":
        zip1 = [i+1 for i in range(len(carted_products))]   #list of 1,2,3,4 till lenght of that carted_products list
        z = zip(carted_products, zip1)  #zips the mentioned lists in one
        return render_template('cart.html',carted_products=carted_products, units=units,z=z)

'''
Removes product from the cart using its id
'''
@app.route('/remove_from_cart/<int:id>', methods=['GET', 'POST'])
def remove_from_cart(id):
    # print('------------',id)
    #removes the product which matches id
    for product in carted_products:
        if product.id==id:
            carted_products.remove(product)
    
    units = {0: 'Kg', 1: 'Liter', 2: 'gram', 3: 'dozen'}
    zip1 = [i+1 for i in range(len(carted_products))]
    z = zip(carted_products, zip1)  #zips the mentioned lists
    return render_template('cart.html',z=z, units=units)

'''
Buyes all products in cart
'''
@app.route('/buy_all/<int:total_products>', methods=['GET', 'POST'])
def buy_all(total_products):
    global prod_quantity
    errors=[]
    total=[]
    units = {0: 'Kg', 1: 'Liter', 2: 'gram', 3: 'dozen'}
    if request.method=="POST" and total_products!=0:
        errors=[]
        product_quantity=[]
        total=[]
        try:
            for i in range(total_products): #capturing and appending quantity list
                if request.form.get(f'product_quantity{i+1}'):  #iteratively captures specified quantities from cart and appends it
                    quantity=request.form.get(f'product_quantity{i+1}')
                    product_quantity.append(float(quantity))
                else:   #if not mentioned it takes it as 1
                    quantity=1
                    product_quantity.append(int(quantity))
                    
            product_quantity_new=product_quantity[::-1]
            zip1 = [i+1 for i in range(total_products)]
            z = zip(carted_products, zip1)
            # print('-------------------', product_quantity)
            for i in range(total_products):
                #lotta debuggers
                # print('---------326---------->', (product_quantity))
                # print('---------327----------', (product_quantity_new))
                # print('----------328---------<', total)
                # print('----------329---------<', total_products)
                # print('----------330-----------',carted_products)
                # print('----------331-----------',zip1)
                
                if carted_products[i].quantity < product_quantity_new[i]:   #users quantity greater tah inventry appends error list
                    errors.append(f"Your need is greater than {carted_products[i].product_name}'s available quantity. Only {carted_products[i].quantity} unit/s remaining...")
                #calculates cost to be paid for each product buyed
                total.append(carted_products[i].price*product_quantity[i])
            if errors:
                return render_template('cart.html',z=z, units=units, errors=errors)
            # print('----------342---------<', total)
            
            zipp = zip(carted_products, total, product_quantity)
            prod_quantity=product_quantity[:]   #copies the list
            # print('---------326---------->', product_quantity)
            
            GrandTotal=sum(total)   #sum of all carted products
            return render_template('buy_all.html',zipp=zipp, units=units, GrandTotal=GrandTotal, product_quantity=product_quantity)
        except:
            errors.append('Please enter valid quantity in integer or decimal format')
            return render_template('cart.html', units=units, errors=errors)
            
    else:
        errors=['no items in cart...']
        return render_template('cart.html', units=units, errors=errors)
        

'''
Buy route for products
'''
@app.route('/buy/', methods=['POST'])
def buyy():
    global carted_products
    if request.method=="POST":
        # user = User.query.get_or_404(userG[0].id)

        for i, productt in enumerate(carted_products):  #iterates using two lists, captures and updates quantity in inventry 
            # print('---------327---------->', productt)
            product = Product.query.get_or_404(productt.id)
            product.quantity = abs(productt.quantity-prod_quantity[i])
        
        db.session.commit()
        #debugers
        # print('---------666---------->', product.quantity)
        # print('---------327---------->', carted_products)
        # print('---------327---------->', user)

        carted_products=[]  #empty list after all operations are done
        return render_template('test.html' )

'''
Searches products from the store
'''
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method=="POST":
        search=request.form.get('search')
        # print('-------------387------------', search)
        #below lines queries products/categories info
        product = Product.query.filter_by(product_name=search).all()
        product_me_date = Product.query.filter_by(m_and_e_date=search).all()
        try:
            product_price = Product.query.filter_by(price=int(search)).all()
        except:
            product_price=-1    #temperorarily sets to -1 to bypass list errors
        cat_products = Product.query.all()
        category = Category.query.filter_by(category_name=search).all()
        
        #debuggers
        # print(category,'---------------',product,'------------',userG[0],'-------------',cat_products)
        # print('-------------------------')
        # print('-------------------------')
        # print('-------------------------')
        # print('------------->>------------', product_me_date, '----------------', product_price)

        units = ['  Rs/Kg', '  Rs/Liter', '  Rs/gram', '  Rs/dozen']
        # print(type(products))
        return render_template('searched_results.html',product_me_date=product_me_date,product_price=product_price, category=category, product=product, units=units, cat_products=cat_products)

'''
Updates username by taking users id
'''
@app.route('/update_username/<int:id>', methods=['GET', 'POST'])
def update_username(id):
    if request.method =="POST":
        msg=None    #success message
        error=None  #error message
        user = User.query.filter_by(id=id).first()
        new_username = request.form.get('update_username')
        #checks necessary conditions and do the correct operations
        if new_username==userG[-1].username:
            error="It's your username dude... ' . '"
        elif not User.query.filter_by(username=new_username).first():
            user.username=new_username
            db.session.commit()
            msg='Username changed successfully!'
        else:
            error='Username already taken...'
        return render_template('profile.html', id=id, msg=msg, user=user, error=error)

'''
Updates password by taking users id
'''
@app.route('/update_password/<int:id>', methods=['GET', 'POST'])
def update_password(id):
    if request.method =="POST":
        msg=None
        error=None
        new_password= request.form['update_password']
        confirm_password = request.form['confirm_password']
        user = User.query.filter_by(id=id).first()
        #checks necessary conditions and do the correct operations
        if new_password==confirm_password:
            user.password=new_password
            db.session.commit()
            msg='Password changed successfully!'
        else:
            error='Please enter correct password...'
        
        return render_template('profile.html', id=id, msg=msg,error=error, user=user)

'''
Profile route to view current users profile
'''
@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    #takes info of user db and shows it
    user=User.query.filter_by(id=id).first()
    return render_template('profile.html', id=id, user=user)

# ===========================================================================================
# ======================================== Runner ===========================================
# ===========================================================================================

'''
Program execution starts here!
'''
if __name__ == "__main__":  #this py file can't be run if called from somewhere else
    with app.app_context(): #necessary for db initialization
        db.create_all()
        app.run(debug=True) #debug true gives info why error is occuring

from flask import Flask, render_template, redirect, request,session, url_for #import a bunch of importanat functions that are used to build and run the app, 
#render_template is used to render or fetch the HTML templates which is what the user sees when they visit the website, redirect is used to redirect the user to a different page,request handles all the POST and GET requests that are made by the user, session is used to store the user data across all pages securely in the session , url_for is used to generate the URL for any function in the app, this helps alot in places where we might rename the function or change the URL structure, it automatically updates the URL in all places where it is used.
from flask import current_app as app #if you directly import app then it leads to circular import error 
#current_app refers to app.py that is the app object that we created 
from datetime import datetime #handles the time stamps which are used in aspects like parking_time, leaving_time...etc.
from .models import * #imports all the tables, attributes and relations created in models.py
import math #helps us in dealing with the cost and time calculations


@app.route("/login", methods = ["GET", "POST"]) #defines a route for teh login URL and accepts both GET POST requests
def login():
    if request.method == "POST":
        #fetches the emaila and password from the form data 
        email = request.form["email"]
        pwd = request.form["pwd"]
        logged_user = User.query.filter_by(email = email).first() #searches the user table for user by matching the email
        if logged_user:
            if logged_user.password == pwd:
                #if its a valid user, that is, email is found and the password matches, then we store the username in the session
                session["username"] = logged_user.username
                if logged_user.is_admin:
                    #in case the user is an admin that is, is_admin is True, we then redirect to the admin dashboard
                    return redirect(url_for("admin_dash"))
                else:
                    #if its a normal user, we fetch all the reservation made until then and rnder the user dashboard with the user data and the reservation history
                    history = (Reservation.query.filter_by(username=logged_user.username).order_by(Reservation.parking_timestamp.desc()).all())
                    return render_template("user_dash.html",logged_user = logged_user,history = history)
            else:
                #if password dpesnt match, it shows an error message 
                return "Password is incorrect"
        else:
            #if the user is not found, it shows an error message
            return "This user does not exist"


    return render_template("login.html")

#defines the route for register and accepts both GET and POST requests
@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        #When a post request is made by the user, we fetch all the data submitted from the from 
        username = request.form["username"]
        email = request.form["email"]
        pwd = request.form["pwd"]
        fullname = request.form['fullname']
        address = request.form['address']
        pincode = request.form['pincode']
        # checks if a user witht the same email ID or username already exists and throws an error in case its true, this is done because both username and email ID are unique and we cannot have duplicates
        user_name = User.query.filter_by(username = username).first()
        user_email = User.query.filter_by(email = email).first()

        if user_name or user_email:
            return "User already exists!"
        else:
            #if the user does not exist, we create a new user object with the data submitted and it gets added to the database
            user = User(username = username, email = email, password = pwd,full_name = fullname,address = address,pincode = pincode)
            db.session.add(user)
            db.session.commit()
        return "Registered Successfully"
    return render_template("register.html")

#defines the route for creating a new parking lot and acceps both GET and POST requests
@app.route("/new_lot",methods = ["GET", "POST"])
def new_lot():
    if request.method == "POST":
        #when a post request is made by the user, we fetch all the data submitted from the form
        Loc= request.form["Loc"]
        price = request.form["price"]
        address = request.form["address"]
        pincode = request.form["pincode"]
        max_spots = int(request.form["max_spots"])
        #while fetching the opening and closing time, it needs to be in the "%H:%M" format for python to accept it, so we convert the string to a time object
        closingTime = request.form["closingTime"]
        openingTime = request.form["openingTime"]
        closingTime_str = request.form["closingTime"]
        openingTime_str = request.form["openingTime"]
        closingTime = datetime.strptime(closingTime_str, "%H:%M").time()
        openingTime = datetime.strptime(openingTime_str, "%H:%M").time()

        #checks if a parking lot in the same prime location already exists and if it does, it throws an error message
        existing_lot = ParkingLot.query.filter_by(prime_location_name=Loc).first()
        if existing_lot:
            return "Parking Lot with this name already exists!"
        
        else:
            #if the parking lot is unique, all the data submitted by the user is used to create a new parkinglot and the data gets added to the DB
            lot = ParkingLot(prime_location_name = Loc, price = price, address = address, pincode = pincode, maximum_spots = max_spots,closing_time = closingTime, opening_time = openingTime)
            db.session.add(lot)
            db.session.commit()

        # this creates the maximum number of parking spots entered by the user in the form,and shows the status as A which means teh parking spot is available and all this gets added to the db
        for _ in range(max_spots):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)
        db.session.commit()
        return "Parking Lot Created Successfully"
    return render_template("new_lot.html")

#defines the route for teh admin_dashboard and accepts both GET and POST requests
@app.route("/admin_dash", methods = ["GET", "POST"])
def admin_dash():
    #fetches the username of the user that is currently loggen in, if there i sno username, it redirects to the login page
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    #checks if the user is an admin, if not, it returns an access denied message
    logged_user = User.query.filter_by(username=username).first()
    if not logged_user or not logged_user.is_admin:
        return "Access Denied: Admins only"
    #gets all the parking lots stored in the database
    lots = ParkingLot.query.all()
    lot_data = [] #this lisst holds all the detailed data about each lot 

    for lot in lots:
        # Gets all spots that belong to this parking lot
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        statuses = [{'id': spot.id, 'status': spot.status} for spot in spots] #this is a list of dictionaries that holds the id and the status of each lot 
        #basic lot data is added to the lot_data list,which will be used by the frontend to display the data in the form of cards
        lot_data.append({
            'id': lot.id,
            'location': lot.prime_location_name,
            'price': lot.price,
            'address': lot.address,
            'pincode': lot.pincode,
            'occupied': sum(1 for s in statuses if s['status'] == 'O'),
            'total': len(statuses),
            'spots': statuses
        })
    return render_template("admin_dash.html", logged_user=logged_user, lots = lot_data)

#defines the route that allows the admin to update the parking lot details of an existing parking lot, the lot_id which is passed as a parameter in the URL helps us to identify which parking lot is getting updated
@app.route("/edit_lot/<int:lot_id>",methods = ["GET", "POST"])
def edit_lot(lot_id):
    #fetched the parking lot using teh unique lot id that is passed in the URL, if the lot is not found, it returns a 404 not found error
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == "POST":
        # when a post request i smade by the user=, that is the user is done making the changes to the lot, we fetch the same from the form submitted by the user and update these details in the database 
        lot.prime_location_name = request.form["Loc"]
        lot.price = request.form["price"]
        lot.address = request.form["address"]
        lot.pincode = request.form["pincode"]
        lot.maximum_spots = int(request.form["max_spots"])
        #while fetchin the opening and closing time, it needs to be in the "%H:%M" format for python to accept it, so we convert the string to a time object
        closingTime_str = request.form["closingTime"]
        openingTime_str = request.form["openingTime"]
        lot.closing_time = datetime.strptime(closingTime_str, "%H:%M:%S").time()
        lot.opening_time = datetime.strptime(openingTime_str, "%H:%M:%S").time()
        
        db.session.commit()
        return redirect(url_for("admin_dash"))
    return render_template("edit_lot.html", lot=lot)

#defines the route for when the user wants to book a new lot
@app.route("/book_lot/<int:lot_id>", methods=["GET", "POST"])
def book_lot(lot_id):
    # fetches the username from the session to ensure the user is logged in, if the user s not loggen in, redirects to the login page 
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    #Check if user already has any active booking, if so, an error message is shown, for the user to first release the current booking before booking a new one
    active_booking = Reservation.query.filter_by(
        username=username,
        leaving_timestamp=None
    ).first()
    if active_booking: # if the user doesnt have a leaving timestamp, it means the user has an active booking
        return "You already have an active booking. Please release it before booking another."

    lot = ParkingLot.query.get_or_404(lot_id)

    # Find the first available spotvin this lot if there are none, a message is shown telling the user the same
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not spot:
        return "No available spots in this lot."

    if request.method == "POST":
        #if a post request is made, then firstly cost per hour is fetched from the lot detais and shown to the user as pre filled data in the frontend, then a new reservation is created with all teh details submitted by the user in the form
        cost_per_hour = lot.price
        new_booking = Reservation(
            spot_id=spot.id,
            username=username,
            parking_timestamp=datetime.now(),
            leaving_timestamp=None,
            cost_per_hour=cost_per_hour,
            vehicle_number=request.form['Vnumber'],
            approx_hours=int(request.form["approx_hours"]),
            wheelchair_required=request.form.get("wheelchair_req") == "Yes"
        )
        db.session.add(new_booking) #adds the details of new booking to the database
        spot.status = 'O'# updates the status of the parking spot as 'O' which means occupied
        db.session.commit()
        return "Booking Confirmed!"

    return render_template("book_lot.html", spot=spot, lot=lot)


#defines the route for logging out
@app.route("/logout")
def logout():
     #This basically clears out the session and logs out the user and redirects to the login page
    session.clear() 
    return redirect(url_for('login'))

#defines the route for when the user wants to book a new lot
@app.route("/user_dash", methods = ["GET", "POST"])
def user_dash():
    # fetches the username from the session to ensure the user is logged in, if the user s not loggen in, redirects to the login page 
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    #fetched all the user details by querying the user table using the username stored in the session
    logged_user = User.query.filter_by(username=username).first()

    #fetches all the past booking made by this user and arranges them in descending order to display in teh recent parkig history
    history = (Reservation.query.filter_by(username=logged_user.username).order_by(Reservation.parking_timestamp.desc()).all())

    #if the user enters something in the search bar, it filters the parking lots based on the prime location name or pincode, else it fetches all the parking lots
    query = request.args.get('query')
    if query:
        lots = ParkingLot.query.filter((ParkingLot.prime_location_name.ilike( f"%{query}%" )) | (ParkingLot.pincode.ilike( f"%{query}%" ))).all()
    else:
        lots = ParkingLot.query.all()
    for lot in lots:
        #in each lot, this loop counts the numbre of occupied spots and adds it to the lot object
        lot.occupied_spots_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
    return render_template("user_dash.html", logged_user=logged_user, query=query, lots=lots, history=history)

#defines the route for when the user wants to release an occupied lot
@app.route("/user_release_lot/<int:reservation_id>", methods=["POST", "GET"])
def release_spot(reservation_id):
    #fetches the reservation details using the reservation_id passed in the URL, if the reservation is not found, it returns a 404 not found error
    reservation = Reservation.query.get_or_404(reservation_id)
    spot = ParkingSpot.query.get_or_404(reservation.spot_id)

    if request.method == "POST":
        if reservation.leaving_timestamp:
            #if the leaving time sstamp is already set, that means the spot was already released, so we return an error message
            return "This spot has already been released."
        
        #generates the parking release time stamp and the duration of parking 
        leaving_time = datetime.now()
        duration = leaving_time - reservation.parking_timestamp
        total_hours = math.ceil(duration.total_seconds() / 3600)
        total_cost = total_hours * reservation.cost_per_hour

        reservation.leaving_timestamp = leaving_time
        spot.status = 'A' #updates the status of the parking spot as 'A' which means available
        db.session.commit()
        return redirect(url_for('user_dash'))

    #here we calculte the total cost for only that point in time and dont update it in the db to avoid any misunderstanding as in, in case the user just opens the release page and doesnt go back, then that time stamp would wrongly get interpreted as the leaving time, s this doesn't update the reservation leaving timestamp in the database unless the user clicks on the release button
    preview_leaving_time = datetime.now()
    duration = preview_leaving_time - reservation.parking_timestamp
    total_hours = math.ceil(duration.total_seconds() / 3600)
    total_cost = total_hours * reservation.cost_per_hour
    return render_template("user_release_lot.html", reservation=reservation, spot=spot, total_cost=total_cost)

#defines the route for viewing the summary of the user's parking trends and reservaions
@app.route("/summary", methods = ["GET", "POST"])
def summary():
    # fetches the username from the session to ensure the user is logged in, if the user s not loggen in, redirects to the login page 
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    #fetches all the user details and reservations made by this user
    logged_user = User.query.filter_by(username=username).first()
    reservations = Reservation.query.filter_by(username=session["username"]).all()

    #initializing variables to kep track of total reservations, total hours parked, total cost payable and a list to keep the recent history of reservations
    total_reservations = len(reservations)
    total_hours = 0
    total_cost = 0
    recent_history = []
    for res in reservations:
        if res.leaving_timestamp:
            #if teh leaving time stampis set then, this calculates the duration of parking in hours and the total cost payable by the user
            duration = (res.leaving_timestamp - res.parking_timestamp).total_seconds()/3600
            duration = math.ceil(duration)
            cost = duration * res.cost_per_hour
            total_hours += duration
            total_cost += cost
            res.duration = duration
            res.cost = cost
        else:
            #if leaving time stamp is not set, then it means the spot is still occupied, so we set the duration and cost as "-" to indicate that the spot is still occupied and no cost is payable yet
            res.duration = "-"
            res.cost = "-"
        recent_history.append(res)


    return render_template("user_summary.html", logged_user=logged_user, total_reservations=total_reservations, total_hours=total_hours, total_cost=total_cost, recent_history=recent_history)

#defines the route for editing the profile
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    # fetches the username from the session to ensure the user is logged in, if the user s not loggen in, redirects to the login page 
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    logged_user = User.query.filter_by(username=username).first()

    #  Get the 'next' page value from URL query or form data
    next_page = request.args.get('next') or request.form.get('next') or 'user_dash'

    if request.method == "POST":
        # Update user profile fields
        logged_user.full_name = request.form["full_name"]
        logged_user.address = request.form["address"]
        logged_user.pincode = request.form["pincode"]

        # Handles the password update
        new_pwd = request.form.get("new_pwd")
        confirm_pwd = request.form.get("confirm_pwd")

        if new_pwd:  # this will only run if if user filled in a new password annd it makes sure that the new password is not the same as the old password
            if new_pwd == logged_user.password:
                return "New password cannot be the same as the old password!"
            elif new_pwd != confirm_pwd:
                return "Passwords do not match!"
            else:
                logged_user.password = new_pwd

        db.session.commit()
        return redirect(url_for(next_page))  

    return render_template("edit_profile.html", logged_user=logged_user, next=next_page)

#defines the route for the users page in teh admin_dash board
@app.route("/reg_users", methods=["GET","POST"])
def reg_users():
    # fetches the username from the session to ensure the user is logged in, if the user s not loggen in, redirects to the login page 
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    logged_user = User.query.filter_by(username = username).first()
    if not logged_user or not logged_user.is_admin:
        # If the user is not an admin, return an access denied message
        return ("Access denied, Admins Only")
    #displays the details of all the users registered in the database
    users = User.query.filter_by(is_admin=False).all()  # Only normal users
    return render_template("admin_reg_users.html", users=users)

#defines the route for viewing the details of a specific parking spot
@app.route("/view_del/<int:spot_id>")
def view_del(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)#fetches the parking spot using the spot_id passed in the URL, if the spot is not found, it returns a 404 not found error
    lot = ParkingLot.query.get(spot.lot_id)# fetches the parking lot details using the lot_id from the spot object
    return render_template("view-del.html", spot=spot, lot=lot)

#defines the route for deleting a parking spot, it accepts only POST requests so that the user cannot access this page directly by typing the URL in the browser thus preventing accidental and unwanted deletions
@app.route("/delete_spot/<int:spot_id>", methods=["POST"])
def delete_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    
    # Prevents deletion if the spot is occupied and shows an error message
    if spot.status == 'O':
        return "Cannot delete: Spot is currently occupied.", 400
    #else it deletes the spot from the database
    db.session.delete(spot)
    db.session.commit()
    return redirect(url_for("admin_dash"))

#defines the route for deleting a specific parking lot
@app.route("/delete_lot/<int:lot_id>", methods=["POST"])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()

    for spot in spots:
        if spot.status == 'O':
            return "Cannot delete lot: One or more spots are still occupied.", 400

    # Delete reservations first
    for spot in spots:
        Reservation.query.filter_by(spot_id=spot.id).delete()
        db.session.delete(spot)

    db.session.delete(lot)
    db.session.commit()
    return redirect(url_for("admin_dash"))


#defines the route for viewing the details of an occupied parking lot
@app.route("/occ_lot/<int:spot_id>")
def occ_lot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    reservation = Reservation.query.filter_by(spot_id=spot_id, leaving_timestamp=None).first()#fetches the actual reservation details using the spot_id
    user = User.query.filter_by(username=reservation.username).first()#fetches teh detials of the user who has occupied this spot
    lot = ParkingLot.query.get(spot.lot_id)#fetches teh parking lot that this spot belongs to 
    
    return render_template("occ_lot.html", reservation=reservation, user=user, lot=lot)

#defines the route which  lets admins search for parking lots using various criteria like prime location, user ID or vehicle number
@app.route('/admin_search', methods=['GET', 'POST'])
def admin_search():
    #initializing variables store the lots that match the search criteria in this list
    lots = []
    search_query = ""
    select_drop_down = ""

    if request.method == "POST":
        # fetches whatever the admin searched for and also fetches the selected dropdown value from the form
        search_query = request.form.get("search_bar", "").strip()
        select_drop_down = request.form.get("select_drop_down", "")

        if select_drop_down == "2":  # Prime Location
            # if the admin searched by prime location, it filters the ParkingLot table based on the search query
            lots = ParkingLot.query.filter(ParkingLot.prime_location_name.ilike(f"%{search_query}%")).all()

        elif select_drop_down == "1":  # UserID
            # if the admin searched by UserID, it fetches all reservations matching the username
            reservations = Reservation.query.filter(Reservation.username.ilike(f"%{search_query}%")).all()
            lot_ids = list({res.spot.lot_id for res in reservations if res.spot})
            lots = ParkingLot.query.filter(ParkingLot.id.in_(lot_ids)).all()

        elif select_drop_down == "3":  # Vehicle Number
            # if the admin searched by Vehicle Number, it fetches all reservations matching the vehicle number
            reservations = Reservation.query.filter(Reservation.vehicle_number.ilike(f"%{search_query}%")).all()
            lot_ids = list({res.spot.lot_id for res in reservations if res.spot})
            lots = ParkingLot.query.filter(ParkingLot.id.in_(lot_ids)).all()

        # dynamically updates occupied count and all spots to each lot
        for lot in lots:
            lot_spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
            lot.spots_data = [{"id": spot.id, "status": spot.status} for spot in lot_spots]
            lot.occupied = sum(1 for spot in lot_spots if spot.status == 'O')
            lot.total = len(lot_spots)


    return render_template("admin_search.html", lots=lots, search_query=search_query, select_drop_down=select_drop_down, location_name=search_query)

#defines the route which lets the admin view the summary of all parking lots, their revenue and availability
@app.route("/admin_summary")
def admin_summary():
    #fetches all parking lots and stores the details in lists to be used in the frontend for displaying the summary
    lots = ParkingLot.query.all()
    labels = []
    values = []
    available = []
    occupied = []

    for lot in lots:
        #loops through all the parking lots and fetches all the parking spots that belong to that lot
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()

        # performs calculations for revenue and occupancy
        lot_revenue = 0
        occ_count = 0
        for spot in spots:
            if spot.status == 'O':
                occ_count += 1

            reservations = Reservation.query.filter_by(spot_id=spot.id).all()
            for r in reservations:
                if r.parking_timestamp and r.leaving_timestamp:
                    duration_hours = (r.leaving_timestamp - r.parking_timestamp).total_seconds() / 3600
                    lot_revenue += duration_hours * r.cost_per_hour

        #adds the lot's prime location name to labels  and revenue  values lists 
        labels.append(lot.prime_location_name) 
        values.append(round(lot_revenue, 2))

        # calculates the number of occupied and available spots
        total_spots = len(spots)
        occupied.append(occ_count)
        available.append(total_spots - occ_count)

    total = sum(values)
    return render_template("admin_summary.html", labels=labels, values=values, total=total,available=available, occupied=occupied)


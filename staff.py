from flask import *
from database import *
import uuid
staff=Blueprint('staff',__name__)


@staff.route('/staffhome',methods=['get','post'])
def staffhome():
	sname=session['sname']
	sid=session['sid']

	return render_template('staffhome.html',sname=sname)


@staff.route('/staff_view_profile',methods=['get','post'])
def staff_view_profile():
	data={}
	sid=session['sid']
	uname=session['username']
	q="SELECT * FROM staff INNER JOIN login USING(username) where username='%s'"%(uname)
	print(q)
	res=select(q)
	data['updater']=res
	print(res)

	if 'update' in request.form:
		fname=request.form['fname']
		lname=request.form['lname']
		gender=reques.form['gender']
		place=request.form['place']
		phone=request.form['phone']
		email=request.form['email']
		username=request.form['uname']
		print(username)
		pwd=request.form['password']
		q="update staff set username='%s',firstname='%s',lastname='%s',gender='%s,place='%s',phone='%s',email='%s' where staff_id='%s'"%(username,fname,lname,place,phone,email,sid)
		print(q)
		update(q)
		
		q="update login set username='%s',password='%s' where username='%s'"%(username,pwd,uname)
		update(q)
		session['username']=username
		uname=session['username']
		print(uname)
		flash("updated successfully")
		return redirect(url_for('staff.staff_view_profile'))
	return render_template('staff_view_profile.html',data=data)





@staff.route('/staff_manage_vehicle',methods=['get','post'])
def staff_manage_vehicle():
	data={}
	if 'submit' in request.form:
		vehicle=request.form['vehicle']
		f=request.files['img']
		amt=request.form['amt']
		stock=request.form['stock']
		path="static/"+str(uuid.uuid4())+f.filename
		f.save(path)
		
		q="insert into vehicle values(NULL,'%s','%s','%s','%s','active')"%(vehicle,path,amt,stock)
		lid=insert(q)
		flash("ADDED SUCESSFULLY")
		
		return redirect(url_for('staff.staff_manage_vehicle'))

	q="select * from vehicle"
	res=select(q)
	if res:
		data['vehicle']=res
		print(res)
	if 'action' in request.args:
		action=request.args['action']
		id=request.args['id']
	else:
		action=None
	if action=='delete':
		q="delete from vehicle where vehicle_id='%s'"%(id)
		delete(q)
		return redirect(url_for('staff.staff_manage_vehicle'))
	if action=='update':
		q="select * from vehicle where vehicle_id='%s'"%(id)
		data['updater']=select(q)
	if action=='inactive':
		
		q="update vehicle set vstatus='inactive' where vehicle_id='%s'"%(id)
		update(q)
		print(q)
		flash("UPDATED AS INACTIVE")
		return redirect(url_for('staff.staff_manage_vehicle'))
	if action=='active':
		q="update vehicle set vstatus='active' where vehicle_id='%s'"%(id)
		update(q)
		return redirect(url_for('staff.staff_manage_vehicle'))
	if 'update' in request.form:
		vehicle=request.form['vehicle']
		f=request.files['img']
		amt=request.form['amt']
		stock=request.form['stock']
		path="static/"+str(uuid.uuid4())+f.filename
		f.save(path)
		q="update vehicle set vehiclename='%s',image='%s',amt='%s',stock='%s' where vehicle_id='%s'"%(vehicle,path,amt,stock,id)
		update(q)
		return redirect(url_for('staff.staff_manage_vehicle'))
	return render_template('staff_manage_vehicle.html',data=data)

@staff.route('/staff_manage_slots',methods=['get','post'])
def staff_manage_slots():
	data={}
	if 'submit' in request.form:
		td=request.form['td']
		rate=request.form['rate']
		q="select * from timeslot where status='active' and duration='%s'"%(td)
		res=select(q)
		if res:
			flash("ALREADY A SLOT ACTIVE IN TIME DURATION"+td)
			return redirect(url_for('staff.staff_manage_slots'))
		else:
			q="insert into timeslot values(NULL,'%s','%s','active')"%(td,rate)
			lid=insert(q)
			flash("ADDED SUCESSFULLY")
			return redirect(url_for('staff.staff_manage_slots'))

	q="select * from timeslot"
	res=select(q)
	if res:
		data['timeslot']=res
		print(res)
	if 'action' in request.args:
		action=request.args['action']
		id=request.args['id']
	else:
		action=None
	if action=='update':
		q="select * from timeslot where slot_id='%s'"%(id)
		data['updater']=select(q)
	if 'update' in request.form:
		td=request.form['td']
		rate=request.form['rate']
		q="select * from timeslot where status='active' and duration='%s'"%(td)
		res=select(q)
		if res:
			flash("ALREADY A SLOT ACTIVE IN TIME DURATION"+td)
			return redirect(url_for('staff.staff_manage_slots'))
		else:
			q="update timeslot set duration='%s',rate='%s' where slot_id='%s'"%(td,rate,id)
			update(q)
			print(q)
			print("55555555555555555555555")
			return redirect(url_for('staff.staff_manage_slots'))
	if action=='inactive':
		
		q="update timeslot set status='inactive' where slot_id='%s'"%(id)
		update(q)
		flash("UPDATED AS INACTIVE")
		return redirect(url_for('staff.staff_manage_slots'))
	if action=='active':
		q="update timeslot set status='active' where slot_id='%s'"%(id)
		update(q)
		return redirect(url_for('staff.staff_manage_slots'))
	
	return render_template('staff_manage_slots.html',data=data)



@staff.route('/staff_view_bookings',methods=['get','post'])
def staff_view_bookings():
	data={}
	q="select * from ordermaster inner join customer using(customer_id) inner join payment using(omaster_id) where  status!='pending' "
	res=select(q)
	data['orders']=res
	print(res)
	if 'action' in request.args:
		action=request.args['action']
		omaster_id=request.args['omaster_id'] 
	else:
		action=None
	if action=='products':
		q="SELECT *,orderchild.quantity AS orqua,vehicle.`stock` AS proqua FROM orderchild INNER JOIN `ordermaster` USING(`omaster_id`)  INNER JOIN vehicle  USING (vehicle_id)   WHERE `ordermaster`.omaster_id='%s'"%(omaster_id)
		res=select(q)
		data['products']=res
		print(res)
	if action=='conreturn':
		q="update ordermaster set status='return conformed' where omaster_id='%s'"%(omaster_id)	
		update(q)
		q="SELECT *,orderchild.quantity AS orqua,vehicle.`stock` AS proqua FROM orderchild INNER JOIN `ordermaster` USING(`omaster_id`)  INNER JOIN vehicle  USING (vehicle_id)  WHERE `ordermaster`.omaster_id='%s'"%(omaster_id)
		res=select(q)
		for row in res:
			orqua=row['orqua']
			proqua=row['proqua']
			upqua=int(proqua)+int(orqua)
			vehicle_id=row['vehicle_id']
			q="update vehicle set stock='%s' where vehicle_id='%s'"%(upqua,vehicle_id)
			update(q)
		return redirect(url_for('admin.admin_view_bookings'))
	



	if 'submit' in request.form:
		from_date=request.form['from_date']
		to_date=request.form['to_date']
		print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

		q="select * from ordermaster inner join customer using(customer_id) where  status!='pending' AND ( date between '%s' and '%s')"%(from_date,to_date)
		print(q)
		res=select(q)
		data['orders']=res
		print(res)
	
	return render_template("staff_view_bookings.html",data=data)
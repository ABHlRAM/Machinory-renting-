from flask import *
from database import *
import uuid
customer=Blueprint('customer',__name__)
 

@customer.route('/customerhome',methods=['get','post'])
def customerhome():
	cname=session['cname']
	cid=session['cid']
	print(cname)
	return render_template('customerhome.html',cname=cname)


@customer.route('/customer_view_ts',methods=['get','post'])
def customer_view_ts():
	data={}
	cname=session['cname']
	cid=session['cid']
	q="select * from timeslot where status='active'"
	res=select(q)
	print(res)
	data['timeslot']=res
	return render_template('customer_view_ts.html',data=data)




@customer.route('/customer_viewbikes',methods=['get','post'])
def customer_viewbikes():
	data={}
	cname=session['cname']
	cid=session['cid']
	# id=request.args['id']
	# data['id']=id
	# duration=request.args['duration']
	# data['duration']=duration
	# cid=session['cid']
	q="select * from vehicle where vstatus='active'"
	res=select(q)
	if res:
		data['vehicle']=res
		print(res)

	if 'action' in request.args:
		action=request.args['action']
		vid=request.args['vid']
		amt=request.args['amt']
	else:
		action=None
	if action=='book':

		q="SELECT * FROM `ordermaster` WHERE `customer_id`='%s' AND STATUS='pending'"%(cid)
		res=select(q)
		print(res)
		if res:
			if res:
				oid=res[0]['omaster_id']
				q="update ordermaster set total=total+'%s'  WHERE omaster_id='%s'"%(amt,oid)
				res=update(q)
				q="select * from orderchild where vehicle_id='%s' and omaster_id='%s'"%(vid,oid)
				res=select(q)
				if res:
					q="update orderchild set quantity=quantity+1,amount=amount+'%s' where vehicle_id='%s' and omaster_id='%s'"%(amt,vid,oid)
					update(q)
					flash("YOUR CART UPDATED")
					return redirect(url_for("customer.customer_viewbikes"))
		
				else:
					q="insert into orderchild values(NULL,'%s','%s','1','%s')"%(oid,vid,amt)
					insert(q)
					flash("YOUR CART UPDATED")
					return redirect(url_for("customer.customer_viewbikes"))			
			
		else:
			q="insert into ordermaster values(NULL,'%s','pending','%s','pending',0,'pending')"%(cid,amt)
			res=insert(q)
			q="insert into orderchild values(NULL,'%s','%s','1','%s')"%(res,vid,amt)
			insert(q)
			flash("ADD TO YOUR  CART")
			return redirect(url_for("customer.customer_viewbikes"))
	return render_template('customer_viewbikes.html',data=data)




@customer.route('/customer_view_cart',methods=['get','post'])
def customer_view_cart():
	data={}
	cid=session['cid']
	
	q="SELECT *,orderchild.quantity AS orqua,vehicle.`stock` AS proqua FROM orderchild INNER JOIN `ordermaster` USING(`omaster_id`)  INNER JOIN vehicle  USING (vehicle_id)  WHERE `ordermaster`.`customer_id`='%s' AND `ordermaster`.`status`='pending'"%(cid)
	print(q)
	res=select(q)
	
	data['cart']=res
	if res:
		total=res[0]['total']	
		omid=res[0]['omaster_id']

	if 'action' in request.args:
			action=request.args['action']
			vid=request.args['vid']
			ochild_id=request.args['ochild_id']
			vrate=request.args['vrate']
			data['vrate']=vrate
			purqua=request.args['purqua']
			puramt=int(purqua)*int(vrate)
			print(puramt)
			
	else:
		action=None
	if action=="update":
		data['vqua']=int(request.args['vqua'])
		q="select * from vehicle where vehicle_id='%s'"%(vid)
		res=select(q)
		data['pname']=res[0]['vehiclename']
		
	if 'updatequa'  in request.form:
		upquantity=request.form['upqua']
		newamt=int(vrate)*int(upquantity)
		q="update ordermaster set total=total+'%s'-'%s' where omaster_id='%s'"%(newamt,puramt,omid)
		update(q)
		q="update orderchild set quantity='%s',amount='%s' where ochild_id='%s'"%(upquantity,newamt,ochild_id)
		update(q)
		return redirect(url_for('customer.customer_view_cart'))
	if action=='delete':
		q="delete from orderchild where ochild_id='%s' "%(ochild_id)
		delete(q)
		q="update ordermaster set total=total-'%s' where omaster_id='%s'"%(puramt,omid)
		update(q)
		q="SELECT * FROM `orderchild`  WHERE  `orderchild`.`omaster_id`='%s'"%(omid)
		print(q)
		res=select(q)
		if res:
			return redirect(url_for("customer.customer_view_cart"))
		else:
			q="delete from `ordermaster` where omaster_id='%s'"%(omid)
			delete(q)
			return redirect(url_for('customer.customer_view_cart'))	

	if 'action2' in request.args:
		action2=request.args['action2']	
		amt=request.args['amt']
	else:
		action2=None
	if action2=='payment':
		print("++++++++++++++++++++++++++++")
		q="SELECT *,orderchild.quantity AS orqua,vehicle.`stock` AS proqua FROM orderchild INNER JOIN `ordermaster` USING(`omaster_id`)  INNER JOIN vehicle  USING (vehicle_id)  WHERE `ordermaster`.omaster_id='%s'"%(omid)
		print(q)
		res=select(q)
		print(res)
		for row in res:
			orqua=row['orqua']
			vehicle=row['vehiclename']
			proqua=row['proqua']
			if int(proqua)<int(orqua):
				flash(vehicle+" Only Left"+proqua +"Update It On Your Quantity To Purchase")
				return redirect(url_for("customer.customer_view_cart"))
			else:
				data['pay']=amt
	if 'pay' in request.form:
		ndays=request.form['ndays']
		import math
		total=int(request.form['total'])
		q="SELECT *,orderchild.quantity AS orqua,vehicle.`stock` AS proqua FROM orderchild INNER JOIN `ordermaster` USING(`omaster_id`)  INNER JOIN vehicle  USING (vehicle_id)  WHERE `ordermaster`.omaster_id='%s'"%(omid)
		res=select(q)
		for row in res:
			orqua=row['orqua']
			proqua=row['proqua']
			upqua=int(proqua)-int(orqua)
			vehicle_id=row['vehicle_id']
			q="update vehicle set stock='%s' where vehicle_id='%s'"%(upqua,vehicle_id)
			update(q)
		q="update ordermaster set status='advance paid',date=curdate(),total='%s',noofdays='%s' where omaster_id='%s'"%(total,ndays,omid)	
		update(q)
		q="update orderchild set amount=amount*'%s' where omaster_id='%s'"%(ndays,omid)
		update(q)
		import math
		payamt=(total)/2
		q="insert into payment values(NULL,'%s','%s',curdate())"%(omid,payamt)
		insert(q)

		flash("BOOKED SUCESSFULLY")
		return redirect(url_for("customer.customer_view_bookings"))
			

	return render_template('customer_view_cart.html',data=data)





@customer.route('/customer_view_bookings',methods=['get','post'])
def customer_view_bookings():
	cid=session['cid']
	data={}
	q="select * from ordermaster where customer_id='%s' and status in('returned','advance paid','return conformed') "%(cid)
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
	if action=='return':
		pay=request.args['amt']
		q="select * from payment where omaster_id='%s'"%(omaster_id)
		res=select(q)
		import math

		pamt=res[0]['pamt']
		print(pamt)
		data['pamt']=pamt
		data['to']=pay
		data['pay']=float(pay)-float(pamt)

	if action=='extend':
		data['extend']=request.args['amt']
	if 'pay' in request.form:
		q="update ordermaster set status='returned' where omaster_id='%s'"%(omaster_id)	
		update(q)
		return redirect(url_for('customer.customer_view_bookings'))
	if 'extend' in request.form:
		ndays=request.form['ndays']
		# total=request.form['total']
		
		q="SELECT *,orderchild.quantity AS orqua FROM orderchild INNER JOIN `ordermaster` USING(`omaster_id`)  INNER JOIN vehicle  USING (vehicle_id)  WHERE `ordermaster`.omaster_id='%s'"%(omaster_id)
		print(q)
		res=select(q)
		print(res)
		for row in res:
			ochild_id=row['ochild_id']
			orqua=row['orqua']
			print(orqua)
			pamt=row['amt']
			print(pamt,'pamt')
			noofdays=res[0]['noofdays']
			print(noofdays)
			extend=res[0]['extend']
			print(extend,"extend")
			totalday=int(noofdays)+int(ndays)+int(extend)
			print(totalday,'totalday')
			singleday=int(pamt)*int(orqua)
			print("singleday",singleday)
			total=singleday*int(totalday)
			print(total,'total')
			q="update orderchild set amount='%s' where ochild_id='%s'"%(total,ochild_id)
			print(q)
			update(q)
		q="select sum(amount) as samt from orderchild where omaster_id='%s'"%(omaster_id)
		res=select(q)
		import math

		totalamt=res[0]['samt']
		q="update ordermaster set extend=extend+'%s',total='%s' where omaster_id='%s'"%(ndays,totalamt,omaster_id)	
		update(q)
		return redirect(url_for('customer.customer_view_bookings'))
	return render_template('customer_view_bookings.html',data=data)


@customer.route('/customer_timeextend',methods=['get','post'])
def customer_timeextend():
	data={}
	boid=request.args['boid']
	
	if 'submit' in request.form:
		data['amt']=request.form['amt']
		day=request.form['day']
		session['day']=day

	if 'pay' in request.form:
		
		
		q="update booking set extend='%s',status='extended and paid' where booking_id='%s'"%(session['day'],boid)
		update(q)
		return redirect(url_for('customer.customer_view_bookings'))
		flash("EXETENTED")


	return render_template('customer_timeextend.html',data=data)

@customer.route('/print')
def pprint():
	data={}
	cid=session['cid']
	data={}
	
	q="SELECT *,booking.status AS bstatus FROM booking  INNER JOIN timeslot USING(slot_id) INNER JOIN vehicle USING(vehicle_id) WHERE customer_id='%s'"%(cid)
	res=select(q)
	if res:
		data['bookings']=res
		print(res)
	
	return render_template('print.html',data=data)


@customer.route('/customer_view_profile',methods=['get','post'])
def customer_view_profile():
	data={}
	username=session['username']
	print(username)
	q="select * from customer inner join login using(username) where username='%s'"%(username)
	res=select(q)
	print(res)
	data['customer']=res
	if 'submit' in request.form:
		ph=request.form['ph']
		email=request.form['email']
		street=request.form['street']
		district=request.form['district']
		uname=request.form['uname']
		password=request.form['password']
		q="update login set username='%s',password='%s' where username='%s'"%(uname,password,username)
		update(q)
		q="update customer set phone='%s',email='%s',street='%s',district='%s',username='%s' where username='%s' "%(ph,email,street,district,uname,username)
		update(q)
		session['username']=uname
		flash("PROFILE UPDATED")
		return redirect(url_for('customer.customer_view_profile'))
	if 'action' in request.args:
		q="delete login,customer from customer inner join login using(username) where username='%s'"%(username)
		delete(q)
		flash("ACCOUNT DELETED SUCESSFULLY")
		return redirect(url_for('public.home'))
	return render_template('customer_view_profile.html',data=data)
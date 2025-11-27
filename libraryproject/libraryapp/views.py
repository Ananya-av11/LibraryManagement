from django.shortcuts import render,redirect
import re,random,os
from django.contrib import messages
from django.contrib.auth.models import User,auth
from .models import Account,Books,Rental,Purchase
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required



# Create your views here.
def index(request):
    return render(request,'index.html')
def home(request):
    return render(request,'index.html')
def about(request):
    return render(request,'about.html')
def signup(request):
    return render(request,'signup.html')
def user_register_fun(request):
    if request.method == 'POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        uname=request.POST['uname']
        address=request.POST['address']
        phone=request.POST['phone']
        if Account.objects.filter(phone=phone).exists():
            messages.error(request,'phone already exists')
            return redirect('signup')
        if not re.match(r'^\d{10}$',phone):
            messages.info(request,'Invalid phone number. It must be 10 digits long.')
            return redirect('signup')
        email=request.POST['email']
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',email):
            messages.error(request,'Invalid email id. Please enter a valid email (e.g., example@mail.com)')
            return redirect('signup')
        uimg=request.FILES.get('img')
        if User.objects.filter(username=uname) or User.objects.filter(email=email).exists():
            if User.objects.filter(username=uname).exists():
                messages.error(request,'Username already exists')
            else:
                messages.error(request,'email already exists')
            return render(request,'signup.html')
        else:
            usr=User.objects.create_user(first_name=fname,last_name=lname,username=uname,email=email)
            usr.save()
            acc=Account(user=usr,address=address,phone=phone,image=uimg)
            acc.save()
            subject='Regsitration confirmation'
            message='Registration is success ,please wait for admin approval...'
            send_mail(subject,"Hello "+uname+' '+message,settings.EMAIL_HOST_USER,{email})
            messages.success(request,'User registration success. Please wait for admin approval..')
            return redirect('signup')

def loginpage(request):
    return render(request,'loginpage.html')
def login_fun(request):
    if request.method == 'POST':
        uname=request.POST['uname']
        password=request.POST['password']
        user=auth.authenticate(username=uname,password=password)
        if user is not None:
            if user.is_authenticated:
                if user.is_staff:
                    login(request,user)
                    request.session['user']=user.username
                    return redirect('adminhome')
                else:
                    login(request,user)
                    request.session['user']=user.username
                    return redirect('allbooks')
        else:
            messages.error(request,'Invalid Username or Password')
            return redirect('loginpage')
    return render(request,'loginpage.html')





@login_required(login_url='loginpage')
def adminhome(request):
    books=Books.objects.all()
    total_book=books.count()
    users=Account.objects.filter(status=1)
    total_user=users.count()
    returned_book=Rental.objects.filter(returned=1).count()
    purchased_book=Purchase.objects.filter(purchasestatus=1).count()
    lost_book=Rental.objects.filter(lost=1).count()
    notreturned_book=Rental.objects.filter(returned=0,lost=0).count()
    pending=Account.objects.filter(status='0').count()

    overdue_items=Rental.objects.filter(returned=0,lost=0,aviewed=0,duedate__lt=now().date())
    count=overdue_items.count()

    return render(request,'adminhome.html',{
        'pending':pending,'totalbook':total_book,'totaluser':total_user,
        'returned_book':returned_book,'purchased_book':purchased_book,
        'lost_book':lost_book,'notreturned_book':notreturned_book,'count':count
        })
@login_required(login_url='loginpage')
def addbooks(request):
    pending=Account.objects.filter(status='0').count()
    overdue_items=Rental.objects.filter(returned=0,lost=0,aviewed=0,duedate__lt=now().date())
    count=overdue_items.count()
    return render(request,'addbooks.html',{'pending':pending,'count':count})
def add_book(request):
    if request.method == 'POST':
        name=request.POST['bname']
        desc=request.POST['bdesc']
        author=request.POST['bauth']
        pid=request.POST['bpid']
        stock=request.POST['bstock']
        bprice=request.POST['bprice']
        bimg=request.FILES.get('bimg')
        bo=Books(bookname=name,description=desc,authorname=author,publisher_id=pid,stock=stock,price=bprice,bookimage=bimg)
        bo.save()
        messages.info(request,'Book Added')
        return render(request,'addbooks.html')

@login_required(login_url='loginpage')
def approve(request):
    pending=Account.objects.filter(status='0').count()
    overdue_items=Rental.objects.filter(returned=0,lost=0,aviewed=0,duedate__lt=now().date())
    count=overdue_items.count()
    
    acc=Account.objects.all()
    return render(request,'approve.html',{'ac':acc,'pending':pending,'count':count})
def req_approve(request,pk):
    acc=Account.objects.get(id=pk)
    acc.status=1
    acc.save()
    pas=str(random.randint(100000,999999))
    user=acc.user
    user.set_password(pas)
    user.save()
    mail=user.email
    name=user.username
    subject='Admin approved'
    message='username:'+str(name)+"\n"+'password:'+str(pas)+"\n"+'email:'+str(mail)
    send_mail(subject,message,settings.EMAIL_HOST_USER,[user.email])
    messages.info(request,'User approved')
    return redirect('approve')
def req_disapprove(request,pk):
    acc=Account.objects.get(id=pk)
    acc.status=2
    acc.save()
    mail=acc.user.email
    subject="Request Disapproved"
    message=f"Dear {acc.user.first_name} {acc.user.last_name}\nWe regret to inform you that your request has been disapproved"
    send_mail(subject,message,settings.EMAIL_HOST_USER,[mail])
    messages.info(request,'User Disapproved')
    return redirect('approve')

@login_required(login_url='loginpage')
def viewbooks(request):
    overdue_items=Rental.objects.filter(returned=0,lost=0,aviewed=0,duedate__lt=now().date())
    count=overdue_items.count()
    pending=Account.objects.filter(status='0').count()

    book=Books.objects.all()
    return render(request,'viewbooks.html',{'book':book,'pending':pending,'count':count})
def updatebooks(request,pk):
    # rental_items = Rental.objects.all()
    # count = sum(1 for item in rental_items if not item.returned and item.duedate < now().date())
    overdue_items=Rental.objects.filter(returned=0,lost=0,aviewed=0,duedate__lt=now().date())
    count=overdue_items.count()
    pending=Account.objects.filter(status='0').count()

    book=Books.objects.get(id=pk)
    return render(request,'updatebooks.html',{'book':book,'pending':pending,'count':count})
def edit_book(request,pk):
    if request.method == 'POST':
        book=Books.objects.get(id=pk)
        book.bookname=request.POST['bname']
        book.description=request.POST['bdesc']
        book.authorname=request.POST['bauth']
        book.publisher_id=request.POST['bpid']
        book.stock=request.POST['bstock']
        book.price=request.POST['bprice']
        img=request.FILES.get('bimg')
        if img:
            if book.bookimage:
                os.remove(book.bookimage.path)
                book.bookimage=img
        book.save()
        messages.info(request,'Successfully Updated')
        return redirect('viewbooks')
def deletebook(request,pk):
    book=Books.objects.get(id=pk)
    book.delete()
    messages.info(request,'Successfully Deleted')
    return redirect('viewbooks')

@login_required(login_url='loginpage')
def viewuser(request):
    pending=Account.objects.filter(status='0').count()
    # rental_items = Rental.objects.all()
    # count = sum(1 for item in rental_items if not item.returned and item.duedate < now().date())
    overdue_items=Rental.objects.filter(returned=0,lost=0,aviewed=0,duedate__lt=now().date())
    count=overdue_items.count()

    acc=Account.objects.filter(status=1)
    return render(request,'viewuser.html',{'ac':acc,'pending':pending,'count':count})
def delete_user(request,pk):
    acc=Account.objects.get(id=pk)
    usr=acc.user
    acc.delete()
    usr.delete()
    messages.info(request,'Successfully Deleted')
    return redirect('viewuser')

@login_required(login_url='loginpage')
def rentalbooks(request):
    pending=Account.objects.filter(status='0').count()

    rental_books=Rental.objects.all()
    return_status =request.GET.get('status','all')
    if return_status == 'returned':
        rental_books=rental_books.filter(returned=1)
    elif return_status == 'not_returned':
        rental_books=rental_books.filter(returned=0,lost=0)
    elif return_status == 'lost':
        rental_books=rental_books.filter(lost=1)

    rental_items=Rental.objects.filter(returned=0,aviewed=0,lost=0)
    overdue_alert=[]
    count=0
    for item in rental_items:
        if not item.returned and item.duedate < now().date():
            if item.lost:
                lostfine=item.book.price+200
            else:
                lostfine=0
            overdue_days=(now().date()-item.duedate).days
            fine_amount=overdue_days*10
            item.fine=fine_amount+lostfine
            item.save()
            # count+=1
            overdue_alert.append({'user':f"{item.user.first_name} {item.user.last_name}",
                                  'book':item.book.bookname,
                                  'overdue_days':overdue_days,
                                  'fine':fine_amount})
    overdue_items=Rental.objects.filter(returned=0,lost=0,aviewed=0,duedate__lt=now().date())
    count=overdue_items.count()
    overdue_items.update(aviewed=1)
    return render(request,'rentalbooks.html',{'rental_books':rental_books,'pending':pending,'count':count,'return_status':return_status,'overdue_alert':overdue_alert})


@login_required(login_url='loginpage')
def purchasebooks(request):
    pending=Account.objects.filter(status='0').count()
    overdue_items=Rental.objects.filter(returned=0,lost=0,aviewed=0,duedate__lt=now().date())
    count=overdue_items.count()

    items=Purchase.objects.filter(purchasestatus=1)
    return render(request,'purchasebooks.html',{'items':items,'pending':pending,'count':count})


@login_required(login_url='loginpage')
def adminresetpassword(request):
    pending=Account.objects.filter(status='0').count()
    overdue_items=Rental.objects.filter(returned=0,lost=0,aviewed=0,duedate__lt=now().date())
    count=overdue_items.count()
    return render(request,'adminresetpassword.html',{'pending':pending,'count':count})
def admin_resetpassword_fun(request):
    if request.method == 'POST':
        current_pass=request.POST['currentpass']
        new_pass=request.POST['newpass']
        c_pass=request.POST['confirmpass']
        if not request.user.check_password(current_pass):
            messages.error(request, 'Current password is incorrect.')
            return redirect('adminresetpassword')
        if new_pass == c_pass:
            if len(new_pass) < 6 or not any(char.isupper() for char in new_pass) \
                or not any(char.isdigit() for char in new_pass) \
                or not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in new_pass):
                messages.error(request, 'Password must be at least 6 characters long and contain at least one uppercase letter, one digit, and one special character.')
                return redirect('adminresetpassword')
            else:
                uid=request.user.id
                usr=User.objects.get(id=uid)
                usr.set_password(new_pass)
                usr.save()
                # messages.success(request, 'Your password has been successfully updated.')
                return redirect('loginpage')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('adminresetpassword')
    return render(request,'adminresetpassword')





@login_required(login_url='loginpage')
def userhome(request):
    purchased_book=Purchase.objects.filter(user=request.user,purchasestatus=1).count()
    lost_book=Rental.objects.filter(user=request.user,lost=1).count()
    returned_book=Rental.objects.filter(user=request.user,returned=1).count()
    notreturned_book=Rental.objects.filter(user=request.user,returned=0).count()

    purchase_items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
    total_purchase=purchase_items.count()
    rental_count=Rental.objects.filter(user=request.user,returned=0,uviewed=0,lost=0)
    count=0
    for i in rental_count:
        if i.duedate < now().date():
            count+=1
    return render(request,'userhome.html',{
        'ptotal':total_purchase,'count':count,'purchased_book':purchased_book,
        'lost_book':lost_book,'returned_book':returned_book,'notreturned_book':notreturned_book
        })
@login_required(login_url='loginpage')
def allbooks(request):
    query=request.GET.get('q','')
    if query:
        book=Books.objects.filter(bookname__icontains=query) | Books.objects.filter(authorname__icontains=query)
    else:
        book=Books.objects.all()
    
    purchase_items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
    total_purchase=purchase_items.count()
    
    rental_count=Rental.objects.filter(user=request.user,returned=0,uviewed=0,lost=0)
    count=0
    for i in rental_count:
        if i.duedate < now().date():
            count+=1
    return render(request,'allbooks.html',{'book':book,'ptotal':total_purchase,'count':count,'query':query})
@login_required(login_url='loginpage')
def rentbookinfo(request,pk):
    purchase_items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
    total_purchase=purchase_items.count()
    rental_count=Rental.objects.filter(user=request.user,returned=0,uviewed=0,lost=0)
    count=0
    for i in rental_count:
        if i.duedate < now().date():
            count+=1
    rent_item=Books.objects.get(id=pk)
    return render(request,'rentbookinfo.html',{'rentitems':rent_item,'ptotal':total_purchase,'count':count})

def rent_info(request,pk):
    book=Books.objects.get(id=pk)
    if request.method == 'POST':
        period=int(request.POST['rental_period'])
        quantity=int(request.POST['quantity'])
        rental_date=timezone.now().date()
        due_date=rental_date+timedelta(days=period)
        
        if book.stock >= quantity:
            rental,created = Rental.objects.get_or_create(user=request.user,book=book,rentaldate=rental_date,duedate=due_date)
            if not created:
                if book.stock >= rental.quantity+quantity:
                    rental.quantity+=quantity
                    rental.duedate=due_date
                    rental.save()
                else:
                    messages.error(request,f'Only {book.stock} copies available for {book.bookname}')
                    return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                rental.quantity=quantity
                rental.save()
            book.stock-=quantity
            book.save()
            return redirect('rentalhistory')
        else:
            messages.error(request,f'Only {book.stock} copies available for {book.bookname}')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    return render(request,'allbooks.html')


def purchase_book(request,pk):
    book=Books.objects.get(id=pk)
    if book.stock <= 0:
        messages.error(request,'Sorry, This book is out of stock')
        return redirect('allbooks')
    purchase_item, created=Purchase.objects.get_or_create(user=request.user,book=book,purchasedate=timezone.now(),purchasestatus=0)    
    if not created:
        if purchase_item.quantity < book.stock:
            purchase_item.quantity += 1
        else:
            messages.error(request, f'Cannoy add more. Only {book.stock} copies available')
            return redirect('allbooks')
    # book.stock -=1
    # book.save()
    purchase_item.save()
    return redirect('purchasecart')

@login_required(login_url='loginpage')
def purchasecart(request):
    items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
    total_purchase=items.count()
    rental_count=Rental.objects.filter(user=request.user,returned=0,uviewed=0,lost=0)
    count=0
    for i in rental_count:
        if i.duedate < now().date():
            count+=1
    
    total_price=sum(item.book.price * item.quantity for item in items) if items else 0
    return render(request,'purchasecart.html',{'items':items,'totalprice':total_price,'ptotal':total_purchase,'count':count})
def decrement_pquantity(request,pk):
    purchase_item=Purchase.objects.get(id=pk,user=request.user)
    book=purchase_item.book
    if purchase_item.quantity > 1:
        purchase_item.quantity -= 1
        # book.stock+=1
        purchase_item.save()    
    else:
        purchase_item.book.stock+=purchase_item.quantity
        purchase_item.delete()
    # book.save()
    return redirect('purchasecart')
def increment_pquantity(request,pk):
    purchase_item=Purchase.objects.get(id=pk,user=request.user)
    if purchase_item.quantity < purchase_item.book.stock:
        purchase_item.quantity += 1
        purchase_item.save()
    else:
        messages.error(request,f'Cannot add more. Only {purchase_item.book.stock} copies available')
    return redirect('purchasecart')
def remove_pbook(request,pk):
    purchase_item=Purchase.objects.get(id=pk,user=request.user)
    purchase_item.delete()
    return redirect('purchasecart')

@login_required(login_url='loginpage')
def checkoutpage(request):
    items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
    total_purchase=items.count()
    rental_count=Rental.objects.filter(user=request.user,returned=0,uviewed=0,lost=0)
    count=0
    for i in rental_count:
        if i.duedate < now().date():
            count+=1
    
    acc=Account.objects.get(user=request.user)
    total_price =sum(item.book.price * item.quantity for item in items)
    return render(request,'checkoutpage.html',{'ac':acc,'totalprice':total_price,'items':items,'ptotal':total_purchase,'count':count})
def placeorder(request):
    if request.method =='POST':
        items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
        if items.exists():
            
            order_details = "\n".join(
                [f"{item.book.bookname} - ₹{item.book.price} x {item.quantity}" for item in items]
            )
            total_price = sum(item.book.price * item.quantity for item in items)

            for item in items:
                item.book.stock-=item.quantity
                item.book.save()

            subject='Order Confirmation'
            message=(f'Dear User,\n Thank you for your purchase.Here are your order details:\n\n {order_details} \n\n Total Price : ₹{total_price}\n Your order has been successfully placed')
            user_email=request.user.email
            send_mail(subject,message,settings.EMAIL_HOST_USER,[user_email])
            items.update(purchasestatus=1)
            messages.success(request, 'Your order has been placed successfully!')
            return redirect('checkoutpage')
        else:
            messages.error(request, "Your cart is empty. Add items before placing an order.")
            return redirect('allbooks')
    return render(request,'checkoutpage.html')

@login_required(login_url='loginpage')
def rentalhistory(request):
    purchase_items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
    total_purchase=purchase_items.count()
    rent_items=Rental.objects.filter(user=request.user).select_related('book')
    return_status =request.GET.get('status','all')
    if return_status == 'returned':
        rent_items=rent_items.filter(returned=1)
    elif return_status == 'not_returned':
        rent_items=rent_items.filter(returned=0,lost=0)
    elif return_status == 'lost':
        rent_items=rent_items.filter(lost=1)

    rental_items=Rental.objects.filter(user=request.user,uviewed=0,returned=0,lost=0)
    overdue_alert=[]
    count=0
    for item in rental_items:
        if not item.returned and item.duedate < now().date():
            if item.lost:
                lostfine=item.book.price+200
            else:
                lostfine=0
            overdue_days=(now().date()-item.duedate).days
            fine_amount=overdue_days*10
            item.fine=fine_amount+lostfine
            item.save()
            count+=1
            overdue_alert.append({
                                  'book':item.book.bookname,
                                  'overdue_days':overdue_days,
                                  'fine':fine_amount})
    overdue_items=Rental.objects.filter(user=request.user,returned=0,lost=0,uviewed=0,duedate__lt=now().date())
    overdue_items.update(uviewed=1)      
    return render(request,'rentalhistory.html',{'rentitems':rent_items,'ptotal':total_purchase,
                                                'return_status':return_status,'count':count,'overdue_alert':overdue_alert})

def return_book(request,pk):
    rentitems=Rental.objects.get(id=pk)
    if rentitems.book:
        rentitems.book.stock+=rentitems.quantity
        rentitems.book.save()
    rentitems.returned='1'
    rentitems.save()
    messages.info(request,'Book returned successfully')
    return redirect('rentalhistory')
@login_required(login_url='loginpage')
def purchasehistory(request):
    purchase_items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
    total_purchase=purchase_items.count()
    # rent_items=Rental.objects.filter(user=request.user,returned=0,lost=0).select_related('book')
    # total_rent=rent_items.count()
    rental_count=Rental.objects.filter(user=request.user,returned=0,uviewed=0,lost=0)
    count=0
    for i in rental_count:
        if i.duedate < now().date():
            count+=1
    
    items=Purchase.objects.filter(user=request.user,purchasestatus=1).select_related('book')
    return render(request,'purchasehistory.html',{'items':items,'ptotal':total_purchase,'count':count})

@login_required(login_url='loginpage')
def lostbook(request):
    purchase_items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
    total_purchase=purchase_items.count()
    rent_items=Rental.objects.filter(user=request.user,returned=0,lost=0).select_related('book')
    total_rent=rent_items.count()
    rental_count=Rental.objects.filter(user=request.user,returned=0,uviewed=0,lost=0)
    count=0
    for i in rental_count:
        if i.duedate < now().date():
            count+=1
    return render(request,'lostbook.html',{'rentitem':rent_items,'ptotal':total_purchase,'rtotal':total_rent,'count':count})
def report_lost_book(request):
    if request.method == 'POST':
        bookid=request.POST.get('bookid')
        rent_item=Rental.objects.get(user=request.user,book=bookid)
        if rent_item.lost == 1:
            messages.info(request,f"You have already reported '{rent_item.book.bookname}' as lost")
            return redirect('lostbook')
        bprice=rent_item.book.price
        additional_charge=200
        bfine=rent_item.fine
        total_fine=bfine+bprice+additional_charge

        rent_item.lost=1
        rent_item.fine=total_fine
        rent_item.save()
        messages.info(request,f"'{rent_item.book.bookname}' has been reported as lost. Fine : ₹{total_fine}")
        return redirect('lostbook')
    return redirect('lostbook')

@login_required(login_url='loginpage')
def viewprofile(request):
    purchase_items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
    total_purchase=purchase_items.count()
    # rent_items=Rental.objects.filter(user=request.user,returned=0,lost=0).select_related('book')
    # total_rent=rent_items.count()
    acc=Account.objects.get(user=request.user)
    rental_count=Rental.objects.filter(user=request.user,returned=0,uviewed=0,lost=0)
    count=0
    for i in rental_count:
        if i.duedate < now().date():
            count+=1
    return render(request,'viewprofile.html',{'ac':acc,'ptotal':total_purchase,'count':count})

@login_required(login_url='loginpage')
def updateprofile(request,):
    purchase_items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
    total_purchase=purchase_items.count()
    # rent_items=Rental.objects.filter(user=request.user,returned=0,lost=0).select_related('book')
    # total_rent=rent_items.count()
    acc=Account.objects.get(user=request.user)
    rental_count=Rental.objects.filter(user=request.user,returned=0,uviewed=0,lost=0)
    count=0
    for i in rental_count:
        if i.duedate < now().date():
            count+=1
    return render(request,'updateprofile.html',{'ac':acc,'ptotal':total_purchase,'count':count})
def edit_user(request):
    if request.method == 'POST':
        acc=Account.objects.get(user=request.user)
        user=request.user
        user.first_name=request.POST['fname']
        user.last_name=request.POST['lname']
        uname=request.POST['uname']
        if User.objects.filter(username=uname).exclude(pk=user.pk).exists():
            messages.info(request,'This username already exists')
            return redirect('updateprofile')
        user.username=uname
        email=request.POST['email']
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',email):
            messages.error(request,'Invalid email id. Please enter a valid email (e.g., example@mail.com)')
            return redirect('updateprofile')
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request,'This email id already exists')
            return redirect('updateprofile')
        phone=request.POST['phone']
        if Account.objects.filter(phone=phone).exclude(pk=acc.pk).exists():
            messages.error(request,'phone already exists')
            return redirect('updateprofile')
        if not re.match(r'^\d{10}$',phone):
            messages.error(request,'Invalid phone number. It must be 10 digits long.')
            return redirect('updateprofile')
        user.email=email
        user.save()
        acc.address=request.POST['address']
        acc.phone=phone
        uimg=request.FILES.get('img')
        if uimg:
            if acc.image:
                os.remove(acc.image.path)
            acc.image=uimg
        acc.save()
        messages.info(request,'Profile Updated Successfully')
        return redirect('viewprofile')
    return render(request,'userhome.html')

@login_required(login_url='loginpage')
def userresetpassword(request):
    purchase_items=Purchase.objects.filter(user=request.user,purchasestatus=0).select_related('book')
    total_purchase=purchase_items.count()
    # rent_items=Rental.objects.filter(user=request.user,returned=0,lost=0).select_related('book')
    # total_rent=rent_items.count()
    rental_count=Rental.objects.filter(user=request.user,returned=0,uviewed=0,lost=0)
    count=0
    for i in rental_count:
        if i.duedate < now().date():
            count+=1   

    return render(request,'userresetpassword.html',{'ptotal':total_purchase,'count':count})
def user_resetpassword_fun(request):
    if request.method == 'POST':
        current_pass=request.POST['currentpass']
        new_pass=request.POST['newpass']
        c_pass=request.POST['confirmpass']
        if not request.user.check_password(current_pass):
            messages.error(request, 'Current password is incorrect.')
            return redirect('userresetpassword')
        if new_pass == c_pass:
            if len(new_pass) < 6 or not any(char.isupper() for char in new_pass) \
                or not any(char.isdigit() for char in new_pass) \
                or not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in new_pass):
                messages.error(request, 'Password must be at least 6 characters long and contain at least one uppercase letter, one digit, and one special character.')
                return redirect('userresetpassword')
            else:
                uid=request.user.id
                usr=User.objects.get(id=uid)
                usr.set_password(new_pass)
                usr.save()
                # messages.success(request, 'Your password has been successfully updated.')
                return redirect('loginpage')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('userresetpassword')
    return render(request,'userresetpassword')

# def usernotification(request):
#     rental_items=Rental.objects.filter(user=request.user)
#     overdue_alert=[]
#     count=0
#     for item in rental_items:
#         if not item.returned and item.duedate < now().date():
#             if item.lost:
#                 lostfine=item.book.price+200
#             else:
#                 lostfine=0
#             overdue_days=(now().date()-item.duedate).days
#             fine_amount=overdue_days*10
#             item.fine=fine_amount+lostfine
#             item.save()
#             count+=1
#             overdue_alert.append({
#                                   'book':item.book.bookname,
#                                   'overdue_days':overdue_days,
#                                   'fine':fine_amount})
#     return render(request,'unotification.html',{'overdue_alert':overdue_alert,'count':count})

def logoutfun(request):
    auth.logout(request)
    return redirect('index')
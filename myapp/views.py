import datetime


from PIL import Image
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
import os
import pickle
from django.conf import settings

MODEL_PATH = os.path.join(settings.BASE_DIR, 'enhanced_toxic_model.pkl')
from keras import *

# Create your views here.
from myapp.models import *

def login_get(request):
    return render(request, 'loginindex.html')
def login_post(request):

    username = request.POST['username']
    password = request.POST['password']

    u = authenticate(request, username=username, password=password)

    if u is not None:
        login(request, u)
        request.session['lid'] = u.id

        if u.groups.filter(name="Admin").exists():
            messages.success(request, 'Login Success')
            return redirect('/myapp/home/')
        else:
            messages.error(request, "User profile not found.")
            return redirect('/myapp/login_get/')

    else:
        messages.error(request, "Invalid username or password.")
        return redirect('/myapp/login_get/')




def forgotpw(request):
    return render(request, 'forgot password.html')

def forgotpw_post(request):
    username = request.POST['textfield']
    return HttpResponse("success")

@login_required
def home(request):
    return render(request,'homeindex.html')


@login_required(login_url='/myapp/login_get/')
def changepw(request):
    return render(request, 'change password.html')

def changepw_post(request):
    cpass = request.POST['textfield']
    npass = request.POST['textfield2']
    cm_pass = request.POST['textfield3']
    user = request.user
    if not user.check_password(cpass):
        messages.error(request, "Current password is incorrect.")
        return redirect('/myapp/changepw/')
    elif npass != cm_pass:
        messages.error(request, "Passwords do not match.")
        return redirect('/myapp/changepw/')

    else:
        user.set_password(npass)
        user.save()
        logout(request)
        messages.success(request, "Password changed successfully! Please log in again.")
        return redirect('/myapp/login_get/')


@login_required
def viewuserdetails(request):
    vi=UserProfile.objects.all()
    return render(request, 'View user details.html',{"data":vi})

def viewuserdetails_post(request):
    search=request.POST['textfield']
    vi = UserProfile.objects.filter(username__icontains=search)
    return render(request, 'View user details.html', {"data": vi})


def viewcomplaints(request):
    cc = Complaints.objects.all()
    return render(request, 'view complaint.html',{"data":cc})

# def viewcomplaints_post(request):
#     fromdate=request.POST['textfield']
#     todate=request.POST['textfield2']
#     searchuser=request.POST['textfield3']
#     if searchuser=='':
#         cc = Complaints.objects.filter(date__range=[fromdate,todate])
#     if fromdate and todate=='':
#         cc = Complaints.objects.filter(USER__email__icontains=searchuser)
#     else:
#         cc = Complaints.objects.filter(date__range=[fromdate,todate],USER__email__icontains=searchuser)
#
#     return render(request, 'view complaint.html', {"data": cc})




from django.shortcuts import render
from .models import Complaints


def viewcomplaints_post(request):
    fromdate = request.POST['textfield']
    todate = request.POST['textfield2']
    searchuser = request.POST['textfield3']
    if searchuser == '' and fromdate != '' and todate != '':
        cc = Complaints.objects.filter(date__range=[fromdate, todate])
    elif fromdate == '' and todate == '' and searchuser != '':
        cc = Complaints.objects.filter(USER__email__icontains=searchuser)
    else:
        cc = Complaints.objects.filter(date__range=[fromdate, todate], USER__email__icontains=searchuser)

    return render(request, 'view complaint.html', {"data": cc})


def sendreply(request,cid):
    return render(request, 'send reply.html',{"cid":cid})
def sendreply_post(request):
    reply=request.POST['textfield']

    cid=request.POST['cid']
    res=Complaints.objects.filter(id=cid).update(reply=reply,status="replied")
    return redirect('/myapp/viewcomplaints/')
def viewreview(request):
    rr = Review.objects.all()
    return render(request, 'app review & rating.html',{"data": rr})
def viewreview_post(request):
    fromdate = request.POST['textfield']
    todate = request.POST['textfield2']
    rr = Review.objects.filter(date__range=[fromdate, todate])
    return render(request, 'app review & rating.html',{"data":rr})



def adviewcomments(request):
    ad=Comments.objects.filter(type='toxic')
    return render(request,'view comments.html',{'data':ad})


def blockuser(request,id,pid,cid):
    Request.objects.filter(Q(FROM__id=id,TO__id=pid) | Q(FROM__id=pid,TO__id=id)).delete()
    Comments.objects.filter(id=cid).delete()
    return HttpResponse('''<script>alert("Removed");window.location='/myapp/adviewcomments/'</script>''')


# -------------------------user----------------------


def user_register(request):
    name =request.POST['name']
    # lastname =request.POST['lastname']
    email =request.POST['email']
    dob =request.POST['dateofbirth']
    place =request.POST['country']
    gender =request.POST['gender']
    phone =request.POST['phonenumber']
    image =request.FILES['image']
    bio =request.POST['pin']
    password=request.POST['password']
    confirmpassword=request.POST['confirmpassword']

    import datetime

    fs = FileSystemStorage()
    date = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '-1.jpg'
    fs.save(date, image)
    path = fs.url(date)

    if User.objects.filter(username=email).exists():
        return JsonResponse({'status': 'no'})



    user = User.objects.create(username=email, password=make_password(password))
    user_group, created = Group.objects.get_or_create(name='UserProfile')
    user.groups.add(user_group)
    user.save()

    uobj=UserProfile()
    uobj.username=name
    uobj.name=name
    uobj.email=email
    uobj.phone=phone
    uobj.photo=path
    uobj.bio=bio
    uobj.place=place
    uobj.gender=gender
    uobj.dob=dob
    uobj.LOGIN=user
    uobj.save()

    return JsonResponse({'status': 'ok'})


def user_login(request):


    username = request.POST['username']
    password = request.POST['password']
    print(username, password)

    u = authenticate(request, username=username, password=password)
    print(u)

    if u is not None:
        request.session['lid'] = request.user.id
        login(request, u)

        lid=u.id

        if u.groups.filter(name="UserProfile").exists():
            bu=UserProfile.objects.get(LOGIN_id=lid)

            if bu.status=='blocked':
                return JsonResponse({'status': 'blocked'})

            return JsonResponse({'status': 'ok','lid':str(lid)})


        else:
            return JsonResponse({'status': 'not ok'})

    else:
        return JsonResponse({'status': 'not ok'})


def user_viewprofile(request):
    lid=request.POST['lid']
    data=UserProfile.objects.get(LOGIN_id=lid)
    return JsonResponse({'status': 'ok',
                         'name':data.username,
                         'email':data.email,
                         'phone':data.phone,
                         'image':data.photo,
                         'pin':data.bio,
                         'post':"",
                         'place':data.place,
                         'gender':data.gender,
                         'dob':data.dob,
                         'account_type':data.account_type,
                         })


def add_public_account(request):
    lid=request.POST['lid']
    UserProfile.objects.filter(LOGIN_id=lid).update(account_type='public')
    return JsonResponse({'status': 'ok'})



def add_private_account(request):
    lid=request.POST['lid']
    UserProfile.objects.filter(LOGIN_id=lid).update(account_type='private')
    return JsonResponse({'status': 'ok'})


def user_viewprofileandeditprofile(request):
    lid =request.POST['lid']
    name =request.POST['name']
    gender =request.POST['gender']
    email =request.POST['email']
    phone =request.POST['phone']
    pin =request.POST['pin']
    post =request.POST['post']
    dob =request.POST['dob']


    if User.objects.filter(username=email).exclude(id=lid):
        return JsonResponse({'status': 'no'})


    obj=UserProfile.objects.get(LOGIN_id=lid)

    if 'image' in request.FILES:
        image = request.FILES['image']
        fs = FileSystemStorage()
        date = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '-1.jpg'
        fs.save(date, image)
        path = fs.url(date)
        obj.photo = path
        obj.save()

    obj.username=name
    obj.email=email
    obj.phone=phone
    obj.post=post
    obj.status=''
    obj.account_type=''
    obj.bio=pin
    obj.gender=gender
    obj.dob=dob
    obj.save()

    return JsonResponse({'status': 'ok'})

def user_chnagepassword(request):
    oldpassword = request.POST['oldpassword']
    newpassword = request.POST['newpassword']
    confirmpassword = request.POST['confirmpassword']
    lid = request.POST['lid']
    user=User.objects.get(id=lid)
    if not user.check_password(oldpassword):
        messages.error(request, "Current password is incorrect.")
        return JsonResponse({'status': 'not ok'})
    elif newpassword != confirmpassword:
        messages.error(request, "Passwords do not match.")
        return JsonResponse({'status': 'not ok'})

    else:
        user.set_password(newpassword)
        user.save()
    return JsonResponse({'status': 'ok'})


# def user_addpost(request):
#     newpost =request.POST['newpost']
#     caption=request.POST['caption']
#     lid=request.POST['lid']
#
#     import datetime
#     import base64
#
#     #
#     date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#     a = base64.b64decode(newpost)
#     fh = open("C:\\Users\\SHIBILA\\.PyCharm2017.1\\media\\userpost\\" + date + ".jpg", "wb")
#     # fh = open("C:\\Users\\91815\\PycharmProjects\\cyber\\media\\" + date + ".jpg", "wb")
#     path = "/media/userpost/" + date + ".jpg"
#     fh.write(a)
#     fh.close()
#
#     # import datetime
#     # import base64
#     # #
#     # date = "post/"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+'jpg'
#     # a = base64.b64decode(newpost)
#     # open(r'C:\\Users\\SHIBILA\\.PyCharm2017.1\\media\\post\\'+date+'wb').write(a)
#     #
#     # # fh = open(r"C:\\Users\\SHIBILA\\.PyCharm2017.1\\media\\post\\" + date + ".jpg", "wb")
#     # # fh = open("C:\\Users\\91815\\PycharmProjects\\cyber\\media\\" + date + ".jpg", "wb")
#     # path = "/media/post/" + date + ".jpg"
#     # fh
#     # fh.close()
#
#     obj=uploadpost()
#     obj.USER=UserProfile.objects.get(LOGIN_id=lid)
#     obj.post=path
#     obj.caption=caption
#     from datetime import datetime
#     obj.date=datetime.now()
#     obj.save()
#     return JsonResponse({'status': 'ok'})
#

#
#
# import os
# import face_recognition
# from django.core.files.storage import FileSystemStorage
# from django.http import JsonResponse
# from django.conf import settings
# from PIL import Image
# import cv2
# import numpy as np
#
#
# def useraddpost(request):
#     try:
#         # Check if it's a POST request
#         if request.method != 'POST':
#             return JsonResponse({"status": "error", "message": "Only POST method allowed"})
#
#         # Validate required fields
#         if 'newpost' not in request.FILES:
#             return JsonResponse({"status": "error", "message": "No image provided"})
#
#         newpost = request.FILES['newpost']
#         caption = request.POST.get('caption', '')
#         loc = request.POST.get('loc', '')
#         lid = request.POST.get('lid')
#
#         if not lid:
#             return JsonResponse({"status": "error", "message": "Login ID required"})
#
#         # Generate unique filename
#         original_name = newpost.name
#         file_extension = os.path.splitext(original_name)[1].lower()
#         if not file_extension:
#             file_extension = '.jpg'
#
#         dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + file_extension
#
#         fs = FileSystemStorage()
#         filename = fs.save(f"post/{dt}", newpost)
#         path = fs.url(filename)
#
#         # Create post object
#         date = datetime.datetime.now().strftime('%Y-%m-%d')
#         obj = Post()
#         obj.photo = path
#         obj.location = loc
#         obj.caption = caption
#         obj.date = date
#         obj.USER = UserProfile.objects.get(LOGIN_id=lid)
#         obj.save()
#
#         # Face recognition for notifications - FIXED FOR CHARFIELD
#         u = UserProfile.objects.all().exclude(LOGIN_id=lid)
#         uids = []
#         imgs = []
#
#         media_root = settings.MEDIA_ROOT
#
#         for user in u:
#             try:
#                 # Since photo is CharField, it contains the file path as string
#                 if user.photo and user.photo.strip():
#                     # Remove /media/ from the beginning if present
#                     photo_path = user.photo
#                     if photo_path.startswith('/media/'):
#                         photo_path = photo_path[7:]  # Remove '/media/'
#                     elif photo_path.startswith('media/'):
#                         photo_path = photo_path[6:]  # Remove 'media/'
#
#                     user_photo_path = os.path.join(media_root, photo_path)
#
#                     print(f"Processing user {user.id}, photo path: {user_photo_path}")
#
#                     if os.path.exists(user_photo_path):
#                         try:
#                             # Load and process image
#                             image = face_recognition.load_image_file(user_photo_path)
#
#                             # Convert image to RGB if needed
#                             if len(image.shape) == 2:  # Grayscale
#                                 image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
#                             elif image.shape[2] == 4:  # RGBA
#                                 image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
#
#                             # Get face encodings
#                             face_encodings = face_recognition.face_encodings(image)
#
#                             if face_encodings:
#                                 imgs.append(face_encodings[0])
#                                 uids.append(user.id)
#                                 print(f"✅ Added encoding for user {user.id}")
#                             else:
#                                 print(f"❌ No faces found for user {user.id}")
#                         except Exception as img_error:
#                             print(f"❌ Image processing error for user {user.id}: {str(img_error)}")
#                     else:
#                         print(f"❌ Photo file not found for user {user.id}: {user_photo_path}")
#                 else:
#                     print(f"❌ No photo path for user {user.id}")
#
#             except Exception as e:
#                 print(f"❌ Error processing user {user.id}: {str(e)}")
#                 continue
#
#         print(f"✅ Loaded {len(imgs)} face encodings from {len(uids)} users")
#
#         # Process the uploaded post image for face recognition
#         post_image_relative_path = filename
#         post_image_full_path = os.path.join(media_root, post_image_relative_path)
#
#         print(f"🔍 Processing post image: {post_image_full_path}")
#
#         if os.path.exists(post_image_full_path):
#             try:
#                 # Load the post image
#                 unknown_image = face_recognition.load_image_file(post_image_full_path)
#
#                 # Convert image to proper format
#                 if len(unknown_image.shape) == 2:  # Grayscale
#                     unknown_image = cv2.cvtColor(unknown_image, cv2.COLOR_GRAY2RGB)
#                 elif unknown_image.shape[2] == 4:  # RGBA
#                     unknown_image = cv2.cvtColor(unknown_image, cv2.COLOR_RGBA2RGB)
#
#                 # Get face encodings and locations
#                 face_encodings = face_recognition.face_encodings(unknown_image)
#                 face_locations = face_recognition.face_locations(unknown_image)
#
#                 print(f"✅ Found {len(face_encodings)} faces in post image")
#
#                 if face_encodings and imgs:
#                     # Open image for modification
#                     imagenews = Image.open(post_image_full_path)
#
#                     # Convert to RGB if necessary
#                     if imagenews.mode in ('RGBA', 'LA', 'P'):
#                         background = Image.new('RGB', imagenews.size, (255, 255, 255))
#                         if imagenews.mode == 'P':
#                             imagenews = imagenews.convert('RGBA')
#                         background.paste(imagenews, mask=imagenews.split()[-1] if imagenews.mode == 'RGBA' else None)
#                         imagenews = background
#                     elif imagenews.mode != 'RGB':
#                         imagenews = imagenews.convert('RGB')
#
#                     def modify_pixel(pixel):
#                         """Modify pixel values for face obfuscation"""
#                         return (pixel[0] ^ 124, pixel[1] ^ 178, pixel[2] ^ 167)
#
#                     # Process each detected face
#                     for m, (face_encoding, face_location) in enumerate(zip(face_encodings, face_locations)):
#                         top, right, bottom, left = face_location
#
#                         print(f"👤 Processing face {m+1}: top={top}, right={right}, bottom={bottom}, left={left}")
#
#                         # Compare with known faces
#                         matches = face_recognition.compare_faces(imgs, face_encoding, tolerance=0.45)
#
#                         print(f"🔍 Face {m+1} matches: {matches}")
#
#                         for i, match in enumerate(matches):
#                             if match and i < len(uids):
#                                 try:
#                                     print(f"🎯 Match found! Creating notification for user ID: {uids[i]}")
#
#                                     # Create notification
#                                     p = Notifications()
#                                     p.POST = obj
#                                     p.USER_id = uids[i]
#                                     p.status = "pending"
#                                     p.date = datetime.now().date()
#                                     p.time = datetime.now().time()
#                                     p.bottom = bottom
#                                     p.left = left
#                                     p.right = right
#                                     p.top = top
#                                     p.save()
#
#                                     # Modify pixels for matched faces (obfuscation)
#                                     for x in range(max(0, left), min(imagenews.width, right)):
#                                         for y in range(max(0, top), min(imagenews.height, bottom)):
#                                             try:
#                                                 pixel = imagenews.getpixel((x, y))
#                                                 new_pixel = modify_pixel(pixel)
#                                                 imagenews.putpixel((x, y), new_pixel)
#                                             except Exception as pixel_error:
#                                                 continue
#
#                                     print(f"✅ Notification created and face obfuscated for user {uids[i]}")
#
#                                 except Exception as notif_error:
#                                     print(f"❌ Error creating notification: {str(notif_error)}")
#                                     continue
#
#                     # Save modified image
#                     imagenews.save(post_image_full_path, quality=95)
#                     print("✅ Post image processed and saved successfully")
#                 else:
#                     if not face_encodings:
#                         print("ℹ️ No faces detected in post image")
#                     if not imgs:
#                         print("ℹ️ No face encodings available for comparison")
#
#             except Exception as e:
#                 print(f"❌ Error processing post image: {str(e)}")
#                 import traceback
#                 traceback.print_exc()
#         else:
#             print(f"❌ Post image not found: {post_image_full_path}")
#
#         return JsonResponse({"status": "ok", "message": "Post created successfully"})
#
#     except UserProfile.DoesNotExist:
#         return JsonResponse({"status": "error", "message": "User not found"})
#     except Exception as e:
#         print(f"❌ Unexpected error in useraddpost: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({"status": "error", "message": f"Internal server error: {str(e)}"})
#


##################################### POST

import os
import face_recognition
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.conf import settings
from PIL import Image
import cv2
import datetime
from .models import Post, UserProfile, Notifications  # Make sure to import your models


def useraddpost(request):
    try:
        # Check if it's a POST request
        if request.method != 'POST':
            return JsonResponse({"status": "error", "message": "Only POST method allowed"})

        # Validate required fields
        if 'newpost' not in request.FILES:
            return JsonResponse({"status": "error", "message": "No image provided"})

        newpost = request.FILES['newpost']
        caption = request.POST.get('caption', '')
        loc = request.POST.get('loc', '')
        lid = request.POST.get('lid')

        if not lid:
            return JsonResponse({"status": "error", "message": "Login ID required"})

        # Generate unique filename
        original_name = newpost.name
        file_extension = os.path.splitext(original_name)[1].lower()
        if not file_extension:
            file_extension = '.jpg'

        dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + file_extension

        fs = FileSystemStorage()
        filename = fs.save(f"post/{dt}", newpost)
        path = fs.url(filename)

        # Create post object
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        obj = Post()
        obj.photo = path
        obj.location = loc
        obj.caption = caption
        obj.date = date
        obj.USER = UserProfile.objects.get(LOGIN_id=lid)
        obj.save()

        # Face recognition for notifications
        u = UserProfile.objects.all().exclude(LOGIN_id=lid)
        uids = []
        imgs = []

        media_root = settings.MEDIA_ROOT

        for user in u:
            try:
                # Since photo is CharField, it contains the file path as string
                if user.photo and user.photo.strip():
                    # Remove /media/ from the beginning if present
                    photo_path = user.photo
                    if photo_path.startswith('/media/'):
                        photo_path = photo_path[7:]  # Remove '/media/'
                    elif photo_path.startswith('media/'):
                        photo_path = photo_path[6:]  # Remove 'media/'

                    user_photo_path = os.path.join(media_root, photo_path)

                    print(f"Processing user {user.id}, photo path: {user_photo_path}")

                    if os.path.exists(user_photo_path):
                        try:
                            # Use PIL to open and convert image to proper format
                            pil_image = Image.open(user_photo_path)

                            # Convert to RGB if necessary
                            if pil_image.mode != 'RGB':
                                pil_image = pil_image.convert('RGB')

                            # Convert PIL image to numpy array
                            image = np.array(pil_image)

                            # Ensure it's 8-bit
                            if image.dtype != np.uint8:
                                image = image.astype(np.uint8)

                            print(f"✅ Image loaded - Shape: {image.shape}, Type: {image.dtype}, Mode: {pil_image.mode}")

                            # Get face encodings
                            face_encodings = face_recognition.face_encodings(image)

                            if face_encodings:
                                imgs.append(face_encodings[0])
                                uids.append(user.id)
                                print(f"✅ Added encoding for user {user.id}")
                            else:
                                print(f"❌ No faces found for user {user.id}")

                        except Exception as img_error:
                            print(f"❌ Image processing error for user {user.id}: {str(img_error)}")
                            # Try alternative method
                            try:
                                # Use OpenCV as fallback
                                image = cv2.imread(user_photo_path)
                                if image is not None:
                                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                                    face_encodings = face_recognition.face_encodings(image)
                                    if face_encodings:
                                        imgs.append(face_encodings[0])
                                        uids.append(user.id)
                                        print(f"✅ Added encoding for user {user.id} (OpenCV fallback)")
                                    else:
                                        print(f"❌ No faces found for user {user.id} (OpenCV fallback)")
                                else:
                                    print(f"❌ OpenCV failed to load image for user {user.id}")
                            except Exception as fallback_error:
                                print(f"❌ Fallback also failed for user {user.id}: {str(fallback_error)}")
                    else:
                        print(f"❌ Photo file not found for user {user.id}: {user_photo_path}")
                else:
                    print(f"❌ No photo path for user {user.id}")

            except Exception as e:
                print(f"❌ Error processing user {user.id}: {str(e)}")
                continue

        print(f"✅ Loaded {len(imgs)} face encodings from {len(uids)} users")

        # Process the uploaded post image for face recognition
        post_image_relative_path = filename
        post_image_full_path = os.path.join(media_root, post_image_relative_path)

        print(f"🔍 Processing post image: {post_image_full_path}")

        if os.path.exists(post_image_full_path):
            try:
                # Load the post image using PIL first for better format handling
                pil_unknown_image = Image.open(post_image_full_path)

                # Convert to RGB if necessary
                if pil_unknown_image.mode != 'RGB':
                    pil_unknown_image = pil_unknown_image.convert('RGB')

                # Convert PIL image to numpy array
                unknown_image = np.array(pil_unknown_image)

                # Ensure it's 8-bit
                if unknown_image.dtype != np.uint8:
                    unknown_image = unknown_image.astype(np.uint8)

                print(f"✅ Post image loaded - Shape: {unknown_image.shape}, Type: {unknown_image.dtype}")

                # Get face encodings and locations
                face_encodings = face_recognition.face_encodings(unknown_image)
                face_locations = face_recognition.face_locations(unknown_image)

                print(f"✅ Found {len(face_encodings)} faces in post image")

                if face_encodings and imgs:
                    # Open image for modification (use the same PIL image we already loaded)
                    imagenews = pil_unknown_image.copy()

                    def modify_pixel(pixel):
                        """Modify pixel values for face obfuscation"""
                        return (pixel[0] ^ 124, pixel[1] ^ 178, pixel[2] ^ 167)

                    # Process each detected face
                    for m, (face_encoding, face_location) in enumerate(zip(face_encodings, face_locations)):
                        top, right, bottom, left = face_location

                        print(f"👤 Processing face {m+1}: top={top}, right={right}, bottom={bottom}, left={left}")

                        # Compare with known faces
                        matches = face_recognition.compare_faces(imgs, face_encoding, tolerance=0.45)

                        print(f"🔍 Face {m+1} matches: {matches}")

                        for i, match in enumerate(matches):
                            if match and i < len(uids):
                                try:
                                    print(f"🎯 Match found! Creating notification for user ID: {uids[i]}")

                                    # Create notification
                                    p = Notifications()
                                    p.POST = obj
                                    p.USER_id = uids[i]
                                    p.status = "pending"
                                    p.date = datetime.datetime.now().date()
                                    p.time = datetime.datetime.now().time()
                                    p.bottom = bottom
                                    p.left = left
                                    p.right = right
                                    p.top = top
                                    p.save()

                                    # Modify pixels for matched faces (obfuscation)
                                    for x in range(max(0, left), min(imagenews.width, right)):
                                        for y in range(max(0, top), min(imagenews.height, bottom)):
                                            try:
                                                pixel = imagenews.getpixel((x, y))
                                                new_pixel = modify_pixel(pixel)
                                                imagenews.putpixel((x, y), new_pixel)
                                            except Exception as pixel_error:
                                                continue

                                    print(f"✅ Notification created and face obfuscated for user {uids[i]}")

                                except Exception as notif_error:
                                    print(f"❌ Error creating notification: {str(notif_error)}")
                                    continue

                    # Save modified image
                    imagenews.save(post_image_full_path, quality=95)
                    print("✅ Post image processed and saved successfully")
                else:
                    if not face_encodings:
                        print("ℹ️ No faces detected in post image")
                    if not imgs:
                        print("ℹ️ No face encodings available for comparison")

            except Exception as e:
                print(f"❌ Error processing post image: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ Post image not found: {post_image_full_path}")

        return JsonResponse({"status": "ok", "message": "Post created successfully"})

    except UserProfile.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found"})
    except Exception as e:
        print(f"❌ Unexpected error in useraddpost: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": f"Internal server error: {str(e)}"})


def user_viewothersusers_post(request):
    lid = request.POST['lid']
    name = request.POST["name"]

    # Filter users by name (case-insensitive) and exclude current user
    res = UserProfile.objects.filter(
        username__icontains=name,account_type='public'
    ).exclude(LOGIN_id=lid)

    l = []
    for i in res:
        l.append({
            'id': i.id,
            'name': i.username,
            'image': i.photo,
            'gender': i.gender
        })

    print(l,'ggggggggggggggggggg')
    return JsonResponse({'status': 'ok', 'data': l})



def user_viewothersusers(request):
    lid=request.POST['lid']
    res=UserProfile.objects.exclude(LOGIN_id=lid,account_type='public')
    l=[]
    for i in res:
           l.append({'id':i.id,'name':i.username,'image':i.photo,'gender':i.gender,})
    print(l)
    return JsonResponse({'status': 'ok','data':l})

def user_sendfriendrequest(request):
    lid=request.POST['lid']
    uid=request.POST['uid']
    re=Request.objects.filter(TO=uid,FROM__LOGIN_id=lid) | Request.objects.filter(FROM=uid,TO__LOGIN_id=lid)
    if re.exists():
        return JsonResponse({'status':'no'})
    else:
        r=Request()
        r.FROM = UserProfile.objects.get(LOGIN=lid)
        r.TO = UserProfile.objects.get(pk=uid)
        from datetime import datetime
        r.date = datetime.now().today()
        r.time = datetime.now().time()
        r.status = 'pending'
        r.save()
        return JsonResponse({'status': 'ok'})


def user_viewotherspost(request):
    l = []
    lid = request.POST['lid']

    friend_ids = Request.objects.filter((Q(FROM__LOGIN_id=lid) | Q(TO__LOGIN_id=lid)),status='accepted').values_list('FROM_id', 'TO_id')

    friend_ids = set([uid for pair in friend_ids for uid in pair])

    res = Post.objects.filter(USER__id__in=friend_ids).exclude(USER__LOGIN_id=lid)

    for post in res:
        liked = 'yes' if Like.objects.filter(USER__LOGIN_id=lid, POST_id=post.id).exists() else 'no'
        lcnt = Like.objects.filter(POST_id=post.id).count()

        l.append({
            'id': post.id,
            'date': post.date,
            'post': post.photo,
            'name': post.USER.username,
            'loc': post.location,
            'cap': post.caption,
            'image': post.USER.photo,
            'liked': liked,
            'likes': str(lcnt)
        })
    print(res)

    return JsonResponse({'status': 'ok', 'data': l})


def user_viewownpost(request):
    lid=request.POST['lid']
    res=Post.objects.filter(USER__LOGIN_id=lid)
    l=[]
    for i in res:
        liked = 'no'
        lcnt = Like.objects.filter(POST_id=i.id)

        if Like.objects.filter(USER__LOGIN_id=lid, POST_id=i.id).exists():
            liked = 'yes'
        l.append({'id':i.id,'date':i.date,'post':i.photo,'caption':i.caption,'loc':i.location,'name':i.USER.username,'image':i.USER.photo,'likes': str(len(lcnt))})
    return JsonResponse({'status': 'ok','data':l})




def user_viewotherpost(request):
    lid=request.POST['lid']
    res=Post.objects.filter(USER__account_type='public').exclude(USER__LOGIN_id=lid)
    l=[]
    for i in res:
        liked = 'no'
        lcnt = Like.objects.filter(POST_id=i.id)

        if Like.objects.filter(POST_id=i.id).exists():
            liked = 'yes'
        l.append({'id':i.id,'date':i.date,'post':i.photo,'caption':i.caption,'loc':i.location,'name':i.USER.username,'image':i.USER.photo,'likes': str(len(lcnt))})
    return JsonResponse({'status': 'ok','data':l})









def user_viewapprovedrequest(req):
    lid=req.POST['lid']
    var=Request.objects.filter(status='accepted',FROM__LOGIN_id=lid)
    l=[]
    for i in var:
        l.append({'id':i.id,'date':i.date,'Status':i.status,'name':i.FROM.name})
    print(l)
    return JsonResponse({'status': 'ok','data':l})


def user_viewfriedrequest(requestS):
    lid=requestS.POST['lid']
    res = Request.objects.filter(TO__LOGIN_id=lid,status="pending")
    l = []
    for i in res:
        l.append({'id': i.id, 'name': i.FROM.username, 'image': i.FROM.photo, 'gender': i.FROM.gender,'status': i.status })
    print(lid)
    return JsonResponse({'status': 'ok', 'data': l})


def user_viewreject(request):
    rid=request.post['rid']
    var=Request.objects.filter(id=rid).update(status='rejected')
    return JsonResponse({'status': 'ok'})


def viewfriends(request):
    lid = request.POST['lid']
    uid = UserProfile.objects.get(LOGIN_id=lid)
    print(uid, 'uuuu')

    roj = Request.objects.filter(FROM_id=uid,status='accepted') | Request.objects.filter(TO_id=uid,status='accepted')
    print(roj,'rrrrrrrr')
    user_data = []
    for user in roj:
        if user.TO.id == uid.id:
            user_data.append({
                "image": user.FROM.photo,
                "id": user.id,
                "name": user.FROM.username,
                "ulid": user.FROM.LOGIN_id,
                "gender": user.FROM.gender,
            })
        if user.FROM.id == uid.id:
            user_data.append({
                "image": user.TO.photo,
                "id": user.id,
                "gender": user.TO.gender,
                "ulid": user.TO.LOGIN_id,
                "name": user.TO.username,
            })

    return JsonResponse({"status": "ok", 'data': user_data})




def user_viewfriedlist(requests):
    lid=requests.POST['lid']
    res=Request.objects.filter( Q(TO__LOGIN_id=lid)|Q(FROM__LOGIN_id=lid),status='accepted')
    l=[]
    for i in res:
        l.append({'id': i.id, 'name': i.FROM.username, 'image': i.FROM.photo, 'gender': i.FROM.gender,'status': i.status })
    return JsonResponse({'status': 'ok', 'data': l})


def user_viewcomments(request):
    res=Comments.objects.filter(type='normal')
    l=[]
    for i in res:
        l.append({'id':i.id,'userid':i.UserProfile.id,'uploadpost':i.POST.id , 'comment':i.comment,'date':i.date})
    return JsonResponse({'status': 'ok','data':l})


def user_viewcommentsandreply(request):
    pid=request.POST['pid']
    res=Comments.objects.filter(POST_id=pid,type='normal')
    l=[]
    for i in res:
        l.append({'id':i.id,'userid':i.USER.username,'userphoto':i.USER.photo,'uploadpost':i.POST.id , 'comment':i.comments,'date':i.date})
    return JsonResponse({'status': 'ok','data':l})





# def user_addcomment(request):
#     lid = request.POST['lid']
#     pid = request.POST['postid']
#     comments = request.POST['comment']
#
#     # Import all required modules at the top
#     import warnings
#     import numpy as np
#     import pandas as pd
#     import tensorflow as tf
#     from tensorflow import keras
#     from tensorflow.keras import layers, optimizers
#     from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout
#     from tensorflow.keras.preprocessing.sequence import pad_sequences
#     from tensorflow.keras.preprocessing.text import Tokenizer
#     from tensorflow.keras.models import Sequential
#     from sklearn.model_selection import train_test_split
#     import pickle
#     import datetime
#     import os
#
#     # Suppress warnings
#     def warn(*args, **kwargs):
#         pass
#
#     warnings.warn = warn
#
#     # Clear keras session
#     keras.backend.clear_session()
#
#     # Load your dataset
#     # sms_df = pd.read_csv(r'C:\kochi\Projects\cyberbullyingdetection\spamham.csv')
#     sms_df = pd.read_csv(r'C:\kochi\Projects\cyberbullyingdetection\test new.csv')
#
#     labels = sms_df.values[:, 1]
#     msgs = sms_df.values[:, 0]
#
#     print("Labels:", labels)
#     print("Messages:", msgs)
#
#     # Split the data
#     train_texts, test_texts, train_labels, test_labels = train_test_split(
#         msgs, labels, test_size=0.1, random_state=500
#     )
#
#     # Use the comment for prediction
#     test_texts = [comments]
#
#     VOCABULARY_SIZE = 5000
#     tokenizer = Tokenizer(num_words=VOCABULARY_SIZE)
#     tokenizer.fit_on_texts(train_texts)
#     print("Vocabulary created")
#
#     MAX_SENTENCE_LENGTH = 100
#     print("MAX_SENTENCE LENGTH=", MAX_SENTENCE_LENGTH)
#
#     trainFeatures = tokenizer.texts_to_sequences(train_texts)
#     trainFeatures = pad_sequences(trainFeatures, MAX_SENTENCE_LENGTH, padding='post')
#
#     testFeatures = tokenizer.texts_to_sequences(test_texts)
#     testFeatures = pad_sequences(testFeatures, MAX_SENTENCE_LENGTH, padding='post')
#     print("Tokenizing completed")
#
#     FILTERS_SIZE = 16
#     KERNEL_SIZE = 5
#     EMBEDDINGS_DIM = 10
#     LEARNING_RATE = 0.001
#     BATCH_SIZE = 32
#     EPOCHS = 20
#
#     print("Embedding dimension:", EMBEDDINGS_DIM)
#     print("Feature length:", len(trainFeatures[0]))
#
#     # Use the fixed sequence length instead of calculating maxlen
#     input_length = MAX_SENTENCE_LENGTH
#
#     # Create model with proper input shape
#     model = Sequential()
#     model.add(Embedding(input_dim=VOCABULARY_SIZE + 1,
#                         output_dim=EMBEDDINGS_DIM,
#                         input_length=input_length))
#     model.add(Conv1D(FILTERS_SIZE, KERNEL_SIZE, activation='relu'))
#     model.add(Dropout(0.5))
#     model.add(GlobalMaxPooling1D())
#     model.add(Dropout(0.5))
#     model.add(Dense(8, activation='relu'))
#     model.add(Dense(1, activation='sigmoid'))
#
#     optimizer = optimizers.Adam(learning_rate=LEARNING_RATE)
#     model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
#
#     # Build the model by calling it with some data
#     model.build(input_shape=(None, input_length))
#     print(model.summary())
#
#     # Convert labels to numpy array with proper dtype
#     train_labels = np.array(train_labels).astype('float32')
#
#     # Train the model
#     history = model.fit(trainFeatures, train_labels, batch_size=BATCH_SIZE, epochs=EPOCHS, verbose=1)
#
#     # Save tokenizer
#     with open('tokenizer.pickle', 'wb') as handle:
#         pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
#
#     # Save model using the new Keras format
#     model.save('cyberbullying_model.keras')  # Recommended way in TF 2.13+
#
#     # Alternative: Save as .h5 with proper naming
#     model.save('model.weights.h5')  # Correct format for weights only
#
#     # Make prediction
#     x = model.predict(testFeatures)
#     mm = ''
#
#     for i in x:
#         print("Prediction score:", i[0])
#         if i[0] > 0.6:
#             print("bull")
#             mm = 'bull'
#         else:
#             print("not bull")
#             mm = ''
#     print("Final classification:", mm)
#
#     # Import your Django models
#     from myapp.models import Comments, UserProfile
#     from django.http import JsonResponse
#
#     if mm == '':
#         b = "normal"
#         print(b)
#         obj = Comments()
#         obj.USER = UserProfile.objects.get(LOGIN_id=lid)
#         obj.POST_id = pid
#         obj.comments = comments
#         obj.date = datetime.datetime.now().date()
#         obj.time = datetime.datetime.now().time()
#         obj.type = b
#         obj.save()
#         return JsonResponse({'status': 'ok'})
#     else:
#         b = "toxic"
#         print(b)
#         obj = Comments()
#         obj.USER = UserProfile.objects.get(LOGIN_id=lid)
#         obj.POST_id = pid
#         obj.comments = comments
#         obj.date = datetime.datetime.now().date()
#         obj.time = datetime.datetime.now().time()
#         obj.type = b
#         obj.save()
#
#         # Count toxic comments for this user
#         toxic_count = Comments.objects.filter(USER__LOGIN_id=lid, type="toxic").count()
#         print(f"Toxic comments count for user: {toxic_count}")
#
#         # If user has 3 or more toxic comments, block them
#         if toxic_count >= 3:
#             user_profile = UserProfile.objects.get(LOGIN_id=lid)
#             user_profile.status = 'blocked'  # Assuming you have a 'status' field
#             user_profile.save()
#             print(f"User {lid} has been blocked due to multiple toxic comments")
#             return JsonResponse(
#                 {'status': 'blocked', 'message': 'Your account has been blocked due to multiple toxic comments'})
#
#         return JsonResponse({'status': 'no', 'message': 'Toxic comment detected'})


########################################################  coment




import pandas as pd
import re
import datetime
import pickle
import os
import requests
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from django.http import JsonResponse
from myapp.models import Comments, UserProfile
from scipy.sparse import hstack
from django.conf import settings


class EnhancedToxicDetector:
    """
    🎯 ENHANCED MULTILINGUAL TOXIC DETECTOR
    ========================================
    Detects toxicity in English, Malayalam, Tamil, Hindi & Hinglish
    Works intelligently with context understanding like ChatGPT
    Uses Gemini-2.0-Flash for AI verification
    """

    def __init__(self, gemini_api_key=None):
        self.model = None
        self.vectorizer = None
        self.is_trained = False
        self.gemini_api_key = gemini_api_key

        # Comprehensive toxic keywords database
        self.toxic_keywords = {
            'english': [
                'stupid', 'idiot', 'fool', 'moron', 'dumb', 'dumbass', 'ass', 'asshole',
                'fuck', 'fucking', 'fucker', 'shit', 'bitch', 'bastard', 'dick', 'cock',
                'pussy', 'cunt', 'whore', 'slut', 'motherfucker', 'son of a bitch',
                'piece of shit', 'garbage', 'trash', 'loser', 'retard', 'hate you',
                'kill yourself', 'die', 'go to hell', 'damn you', 'curse you',
                'worthless', 'useless', 'pathetic', 'disgusting', 'ugly', 'fat ass'
            ],
            'malayalam': [
                'മൈരേ', 'പൊട്ടൻ', 'പട്ടി', 'തേണ്ടി', 'തള്ള', 'കുണ്ണ', 'പൂർ', 'പൂറ്',
                'ഊമ്പ്', 'ചാണകം', 'കോഴി', 'പന്നി', 'നായേ', 'ഓളാ', 'മോന്ത',
                'myre', 'myran', 'poda', 'podi', 'punda', 'kunna', 'poor', 'poore',
                'patti', 'thendi', 'thalla', 'kozhi', 'naye', 'oombu', 'chaanakam',
                'pottan', 'panni', 'ola', 'montha', 'poyi', 'poyi olu', 'kotham',
                'loosu', 'muttal', 'maire', 'myru', 'potte', 'theetta'
            ],
            'tamil': [
                'பொறுக்கி', 'சூத்து', 'கூதி', 'ஓத்த', 'நாய்', 'பன்னி', 'ஓழ்',
                'மூடா', 'கழுதை', 'புண்ட', 'சுன்னி', 'பயலே',
                'punda', 'punday', 'koothi', 'soothu', 'otha', 'ommala', 'naai',
                'naye', 'panni', 'paya', 'payale', 'kazhudhai', 'mooda', 'moodra',
                'sunni', 'soole', 'sukku', 'porikki', 'loosu', 'mental', 'oona'
            ],
            'hindi': [
                'चूतिया', 'मादरचोद', 'भोसडीके', 'बहनचोद', 'हरामी', 'कुत्ता', 'गधा',
                'रंडी', 'भड़वा', 'कमीने', 'साला', 'लौड़ा', 'गांड', 'चूत', 'बकवास',
                'chutiya', 'madarchod', 'bhosdike', 'behenchod', 'harami', 'haramzada',
                'kutta', 'kutte', 'gadha', 'randi', 'bhadwa', 'kamine', 'kamina',
                'saala', 'sala', 'lauda', 'loda', 'gaand', 'gandu', 'chut', 'bakwas',
                'bevakoof', 'budhu', 'ullu', 'pagal', 'buddhu', 'faltu'
            ],
            'hinglish': [
                'bloody fool', 'bloody idiot', 'you dog', 'sala kutta', 'stupid fellow',
                'you bastard da', 'fuck you da', 'idiot myre', 'stupid punda',
                'chutiya man', 'bhosdike fellow', 'you harami', 'kutta saala'
            ]
        }

        # Language detection patterns
        self.language_patterns = {
            'malayalam': r'[\u0D00-\u0D7F]',
            'tamil': r'[\u0B80-\u0BFF]',
            'hindi': r'[\u0900-\u097F]'
        }

        print("✅ Enhanced Toxic Detector Initialized (Gemini-2.0-Flash)")

    def detect_language(self, text):
        """Advanced language detection"""
        text_lower = text.lower()

        # Check for script-based languages
        for lang, pattern in self.language_patterns.items():
            if re.search(pattern, text):
                return lang

        # Check for transliterated/mixed content
        if any(word in text_lower for word in self.toxic_keywords['malayalam']):
            return 'malayalam'
        elif any(word in text_lower for word in self.toxic_keywords['tamil']):
            return 'tamil'
        elif any(word in text_lower for word in self.toxic_keywords['hindi']):
            return 'hindi'
        elif any(phrase in text_lower for phrase in self.toxic_keywords['hinglish']):
            return 'hinglish'

        return 'english'

    def keyword_check(self, text):
        """Fast keyword-based toxicity check"""
        text_lower = text.lower().strip()
        text_words = set(text_lower.split())

        detected_toxic_words = []

        # Check all language categories
        for lang, keywords in self.toxic_keywords.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Check for exact word match or phrase match
                if ' ' in keyword_lower:
                    if keyword_lower in text_lower:
                        detected_toxic_words.append((keyword, lang))
                else:
                    if keyword_lower in text_words or keyword_lower in text_lower:
                        detected_toxic_words.append((keyword, lang))

        return len(detected_toxic_words) > 0, detected_toxic_words

    def create_comprehensive_dataset(self):
        """Create comprehensive multilingual training dataset"""
        print("📊 Creating comprehensive training dataset...")

        # Toxic examples from all languages
        toxic_examples = [
            # English
            "you are stupid", "you idiot", "you moron", "fuck you", "you bastard",
            "go to hell", "you are worthless", "kill yourself", "you suck", "stupid fool",
            "you are garbage", "piece of shit", "motherfucker", "dumbass", "asshole",
            "shut up idiot", "you're pathetic", "hate you", "die idiot", "fucking loser",

            # Malayalam (transliterated)
            "poda myre", "poda pulla", "myre", "punda", "thendi", "poyi da",
            "patti", "loosu", "muttal", "kotham", "maire poda", "ni maire",
            "poda potte", "oombu myre", "chaanakam", "kozhi", "thalla",
            "naye", "poda naye", "myru", "montha", "ola maire",

            # Tamil (transliterated)
            "punda", "soothu", "moodra", "naai", "otha", "koothi", "naye punda",
            "payale", "kazhudhai", "sunni", "porikki", "loosu payya", "sukku",
            "mental da", "mooda", "ommala", "oona da", "panni da",

            # Hindi (transliterated)
            "chutiya", "madarchod", "bhosdike", "behenchod", "harami", "kutta",
            "gadha", "randi", "bhadwa", "kamine", "sala kutta", "lauda",
            "gandu", "bevakoof", "budhu sala", "ullu ka pattha", "pagal",

            # Hinglish/Mixed
            "stupid myre", "idiot da", "fuck you punda", "you chutiya fellow",
            "madarchod man", "bhosdike you", "sala idiot", "bloody fool",
            "you dog sala", "kutta stupid", "maire you", "punda stupid"
        ]

        # Normal examples
        normal_examples = [
            # English - Friendly
            "hello", "hi", "thank you", "thanks", "good morning", "good night",
            "nice post", "well done", "great work", "how are you", "good job",
            "excellent", "awesome", "beautiful", "lovely", "perfect", "wonderful",
            "amazing work", "that's great", "cool", "nice", "good", "fine",

            # English - Neutral/Questions
            "what is this", "how to do", "can you help", "please explain",
            "i don't understand", "why is this", "where is it", "when will it happen",
            "ok", "yes", "no", "maybe", "sure", "alright", "i see",

            # Malayalam - Friendly
            "hello", "nandi", "sundaram", "valare nanni", "super", "kidilam",
            "adipoli", "ishtam", "manoharam", "nalla", "kollam", "pwoli",

            # Tamil - Friendly
            "nalla iruku", "romba nandraga", "sari", "nandri", "super",
            "nalla", "miga nalla", "azhaga iruku", "romba nalla",

            # Hindi - Friendly
            "accha hai", "bahut badhiya", "shukriya", "dhanyavad", "khoobsurat",
            "mast hai", "jawab nahi", "umda", "bahut accha",

            # Short responses
            "..", "...", ".", "ok", "yes", "no", "hmm", "aha", "oh", "wow"
        ]

        # Create balanced dataset
        toxic_data = [(text, 1) for text in toxic_examples]
        normal_data = [(text, 0) for text in normal_examples]

        # Balance classes
        max_count = max(len(toxic_data), len(normal_data))

        # Duplicate to balance
        while len(toxic_data) < max_count:
            toxic_data.extend(toxic_data[:max_count - len(toxic_data)])
        while len(normal_data) < max_count:
            normal_data.extend(normal_data[:max_count - len(normal_data)])

        all_data = toxic_data + normal_data
        np.random.shuffle(all_data)

        messages = [item[0] for item in all_data]
        labels = [item[1] for item in all_data]

        print(f"📊 Dataset: {len(toxic_data)} toxic + {len(normal_data)} normal = {len(all_data)} total")
        return pd.DataFrame({'message': messages, 'label': labels})

    def extract_advanced_features(self, text):
        """Extract advanced features from text"""
        text_lower = text.lower()
        words = text_lower.split()

        features = [
            len(text),  # length
            len(words),  # word count
            len(set(words)) / max(len(words), 1),  # unique word ratio
            text_lower.count('!'),  # exclamations
            text_lower.count('?'),  # questions
            text_lower.count('.'),  # dots
            sum(1 for c in text if c.isupper()) / max(len(text), 1),  # uppercase ratio
            int(bool(re.search(r'[\u0D00-\u0D7F]', text))),  # malayalam script
            int(bool(re.search(r'[\u0B80-\u0BFF]', text))),  # tamil script
            int(bool(re.search(r'[\u0900-\u097F]', text))),  # hindi script
            len(re.findall(r'[^\w\s]', text)) / max(len(text), 1),  # special chars
            max(len(word) for word in words) if words else 0,  # longest word
            text_lower.count('you'),  # "you" mentions (personal attacks)
            text_lower.count('your'),  # "your" mentions
            int(any(word in text_lower for word in ['stupid', 'idiot', 'fool'])),  # basic insult indicators
        ]

        return features

    def train_ml_model(self):
        """Train enhanced ML model"""
        print("🤖 Training Enhanced ML Model...")

        df = self.create_comprehensive_dataset()
        texts = df['message'].fillna('').astype(str)
        labels = df['label'].values

        # Extract features
        features_list = []
        for text in texts:
            features = self.extract_advanced_features(text)
            features_list.append(features)

        X_features = np.array(features_list)

        # Advanced TF-IDF Vectorization
        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 5),
            max_features=3000,
            min_df=1,
            lowercase=True,
            sublinear_tf=True
        )

        X_tfidf = self.vectorizer.fit_transform(texts)
        X_combined = hstack([X_tfidf, X_features])

        # Train with Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=20,
            min_samples_split=5,
            class_weight='balanced'
        )

        self.model.fit(X_combined, labels)
        self.is_trained = True

        # Test accuracy
        train_score = self.model.score(X_combined, labels)
        print(f"📊 Model trained with accuracy: {train_score:.4f}")

        self._save_model()
        return True

    def ml_predict(self, text):
        """ML prediction with confidence"""
        if not self.is_trained:
            if not self.load_model():
                return False, 0.5

        try:
            features = self.extract_advanced_features(text)
            X_features = np.array([features])

            X_tfidf = self.vectorizer.transform([text])
            X_combined = hstack([X_tfidf, X_features])

            probability = self.model.predict_proba(X_combined)[0][1]
            is_toxic = probability > 0.5

            return is_toxic, probability

        except Exception as e:
            print(f"❌ ML prediction error: {e}")
            return False, 0.5

    def gemini_verify(self, text, keyword_toxic, keyword_words, ml_toxic, ml_confidence):
        """Gemini-2.0-Flash verification with full context"""
        if not self.gemini_api_key:
            print("   ⚠️  Gemini API key not configured")
            return ml_toxic, ml_confidence, "Gemini not available"

        try:
            # Use Gemini-2.0-Flash model
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_api_key}"

            language = self.detect_language(text)
            keyword_info = f"Detected toxic words: {', '.join([w[0] for w in keyword_words])}" if keyword_words else "No toxic keywords"

            prompt = f"""You are an expert multilingual content moderator. Analyze this text for toxicity/abuse/hate speech.

TEXT: "{text}"
LANGUAGE: {language}
KEYWORD CHECK: {'TOXIC' if keyword_toxic else 'CLEAN'} ({keyword_info})
ML PREDICTION: {'TOXIC' if ml_toxic else 'NORMAL'} (confidence: {ml_confidence:.2f})

TOXICITY RULES (CRITICAL - MUST FOLLOW):

1. EXPLICIT INSULTS (ALWAYS TOXIC):
   - English: stupid, idiot, fool, moron, dumb, fuck, shit, bastard, bitch, asshole, dick, etc.
   - Malayalam: myre, maire, poda, punda, thendi, patti, kotham, loosu, muttal, etc.
   - Tamil: punda, soothu, koothi, otha, naai, naye, mooda, sukku, etc.
   - Hindi: chutiya, madarchod, bhosdike, behenchod, harami, kutta, gadha, randi, etc.

2. CONTEXT MATTERS:
   - Personal attacks = TOXIC ("you are stupid", "you idiot")
   - Mixed language abuse = TOXIC ("poda myre", "stupid fellow", "sala kutta")
   - Friendly phrases = NORMAL ("hello", "thank you", "good work")

3. SHORT MESSAGES:
   - "ok", "yes", "no", "...", "." = NORMAL (unless clearly sarcastic/toxic context)
   - Just symbols without toxic words = NORMAL

4. CRITICAL: If ANY toxic word from above lists is present → HIGH confidence TOXIC

Respond ONLY with this exact JSON format:
{{"is_toxic": true, "confidence": 0.95, "reason": "brief explanation"}}"""

            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 1,
                    "topP": 1,
                    "maxOutputTokens": 256,
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            }

            headers = {'Content-Type': 'application/json'}

            print(f"   🔄 Calling Gemini-2.0-Flash...")
            response = requests.post(url, json=payload, headers=headers, timeout=15)

            if response.status_code == 200:
                result = response.json()

                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]

                    if 'content' in candidate and 'parts' in candidate['content']:
                        content = candidate['content']['parts'][0]['text']
                        print(f"   ✅ Gemini-2.0-Flash responded")

                        # Extract JSON
                        json_match = re.search(r'\{.*?\}', content, re.DOTALL)
                        if json_match:
                            try:
                                gemini_result = json.loads(json_match.group())
                                gemini_toxic = gemini_result.get('is_toxic', ml_toxic)
                                gemini_confidence = float(gemini_result.get('confidence', ml_confidence))
                                reason = gemini_result.get('reason', 'AI analysis')

                                print(
                                    f"   🤖 Gemini: {'TOXIC' if gemini_toxic else 'NORMAL'} ({gemini_confidence:.2f})")

                                # Smart combination
                                if keyword_toxic:
                                    return True, max(0.85, gemini_confidence), f"Toxic keywords: {reason}"
                                elif ml_confidence > 0.8 and gemini_confidence > 0.7:
                                    return ml_toxic, (ml_confidence + gemini_confidence) / 2, reason
                                elif gemini_confidence > 0.85:
                                    return gemini_toxic, gemini_confidence, reason
                                else:
                                    final_toxic = (ml_confidence + gemini_confidence) / 2 > 0.5
                                    final_confidence = (ml_confidence + gemini_confidence) / 2
                                    return final_toxic, final_confidence, reason
                            except json.JSONDecodeError:
                                print(f"   ⚠️  JSON parse error")
                                return ml_toxic, ml_confidence, "ML analysis"

                print(f"   ⚠️  Unexpected response structure")
                return ml_toxic, ml_confidence, "ML analysis"
            else:
                error_msg = response.text[:200]
                print(f"   ❌ API Error {response.status_code}: {error_msg}")
                return ml_toxic, ml_confidence, "ML analysis"

        except requests.exceptions.Timeout:
            print(f"   ⏱️  Gemini API timeout")
            return ml_toxic, ml_confidence, "ML analysis"
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return ml_toxic, ml_confidence, "ML analysis"

    def analyze_comment(self, text):
        """
        🎯 MAIN INTELLIGENCE ANALYSIS
        =============================
        Multi-layer detection:
        1. Keyword Check (Fast & Accurate)
        2. ML Analysis (Pattern Recognition)
        3. Gemini-2.0-Flash (Context Understanding)
        """
        if not text or len(text.strip()) < 1:
            return False, 0.0, "Empty text"

        text = str(text).strip()
        language = self.detect_language(text)

        print(f"\n{'='*60}")
        print(f"🔍 ANALYZING: '{text}'")
        print(f"🌐 Language: {language}")
        print(f"{'='*60}")

        # LAYER 1: KEYWORD CHECK
        print("\n1️⃣ Keyword Analysis...")
        keyword_toxic, toxic_words = self.keyword_check(text)
        if keyword_toxic:
            print(f"   🚨 TOXIC KEYWORDS FOUND: {[w[0] for w in toxic_words]}")
        else:
            print(f"   ✅ No toxic keywords detected")

        # LAYER 2: ML ANALYSIS
        print("\n2️⃣ ML Pattern Analysis...")
        ml_toxic, ml_confidence = self.ml_predict(text)
        print(f"   🤖 ML: {'TOXIC' if ml_toxic else 'NORMAL'} (confidence: {ml_confidence:.3f})")

        # LAYER 3: GEMINI-2.0-FLASH AI
        print("\n3️⃣ AI Context Analysis...")
        final_toxic, final_confidence, reason = self.gemini_verify(
            text, keyword_toxic, toxic_words, ml_toxic, ml_confidence
        )

        # FINAL DECISION
        print(f"\n{'='*60}")
        print(f"🎯 FINAL VERDICT: {'🚨 TOXIC' if final_toxic else '✅ NORMAL'}")
        print(f"📊 Confidence: {final_confidence:.3f}")
        print(f"💡 Reason: {reason}")
        print(f"{'='*60}\n")

        return final_toxic, final_confidence, reason

    def _save_model(self):
        """Save trained model"""
        try:
            model_data = {
                'model': self.model,
                'vectorizer': self.vectorizer,
            }
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump(model_data, f)
            print("💾 Model saved successfully!")
        except Exception as e:
            print(f"❌ Error saving model: {e}")

    def load_model(self):
        """Load trained model"""
        try:
            if os.path.exists(MODEL_PATH):
                with open(MODEL_PATH, 'rb') as f:
                    model_data = pickle.load(f)
                self.model = model_data['model']
                self.vectorizer = model_data['vectorizer']
                self.is_trained = True
                print("✅ Model loaded successfully!")
                return True
            else:
                print("📝 No model found, training new one...")
                return self.train_ml_model()
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return self.train_ml_model()

# DJANGO VIEW
def user_addcomment(request):
    """
    📝 ENHANCED COMMENT HANDLER
    ==========================
    Intelligent multi-layer toxicity detection
    """
    lid = request.POST['lid']
    pid = request.POST['postid']
    comments = request.POST['comment']

    print(f"\n👤 User {lid} submitting: '{comments}'")

    # Initialize detector with Gemini API
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or request.POST.get('api_key')
    detector = EnhancedToxicDetector(gemini_api_key=api_key)

    # Intelligent analysis
    is_toxic, confidence, reason = detector.analyze_comment(comments)

    # Save to database
    obj = Comments()
    obj.USER = UserProfile.objects.get(LOGIN_id=lid)
    obj.POST_id = pid
    obj.comments = comments
    obj.date = datetime.datetime.now().date()
    obj.time = datetime.datetime.now().time()
    obj.type = "toxic" if is_toxic else "normal"
    obj.save()

    print(f"💾 Comment saved as: {obj.type.upper()}")

    # Handle toxic comments
    if is_toxic:
        toxic_count = Comments.objects.filter(USER__LOGIN_id=lid, type="toxic").count()
        print(f"⚠️  User toxic count: {toxic_count}")

        if toxic_count >= 3:
            # Block user after 3 toxic comments
            user_profile = UserProfile.objects.get(LOGIN_id=lid)
            user_profile.status = 'blocked'
            user_profile.save()

            return JsonResponse({
                'status': 'blocked',
                'message': f'Your account has been blocked due to {toxic_count} toxic comments. Please contact support.'
            })

        return JsonResponse({
            'status': 'no',
            'message': f'⚠️ Toxic comment detected! ({toxic_count}/3 warnings)',
            'reason': reason,
            'confidence': round(confidence, 2)
        })

    return JsonResponse({
        'status': 'ok',
        'message': '✅ Comment posted successfully!'
    })



########################################################reply




def user_viewreply(request):
    lid=request.POST['lid']
    r=Complaints.objects.filter(USER__LOGIN_id=lid)
    l=[]
    for i in r:
        l.append({'id':i.id,'date':i.date,'complaint':i.complaints,'reply':i.reply ,'status':i.status})

    return JsonResponse({'status': 'ok','data':l})


def user_sendcomplaint(request):
    lid = request.POST['lid']
    date=datetime.datetime.now().date()
    complaints=request.POST['complaint']
    reply='pending'
    status='pending'

    obj=Complaints()
    obj.USER=UserProfile.objects.get(LOGIN_id=lid)
    obj.date=date
    obj.complaints=complaints
    obj.reply='pending'
    obj.status=status
    obj.save()

    return JsonResponse ({'status':'ok'})
def and_review_rating(request):
    lid = request.POST['lid']
    date=datetime.datetime.now().date()
    re=request.POST['review']
    ra=request.POST['rating']

    obj=Review()
    obj.USER=UserProfile.objects.get(LOGIN_id=lid)
    obj.date=date
    obj.review=re
    obj.rating=ra
    obj.save()

    return JsonResponse ({'status':'ok'})

def user_chatfromfrieds(request):
        return JsonResponse ({'status':'ok'})


def admin_logout(request):
    logout(request)
    return redirect('/myapp/login_get/')


def user_followback(request):
    lid = request.POST['lid']
    uid = request.POST['uid']
    re = Request.objects.filter(TO=uid, FROM__LOGIN_id=lid)
    if re.exists():
        return JsonResponse({'status': 'no'})
    else:
        re = Request.objects.filter(id=uid).update(status='accepted')
        return JsonResponse({'status': 'ok'})



# def user_followback(request):
#
#         uid = request.POST['uid']
#         re = Request.objects.filter(id=uid).update(status='accepted')
#         return JsonResponse({'status': 'ok'})
#
def user_remove(request):
        uid = request.POST['uid']
        re = Request.objects.filter(id=uid).delete()
        return JsonResponse({'status': 'ok'})

def user_fromremovefromfriendlist(request):
        uid = request.POST['uid']
        print(uid)
        re = Request.objects.get(id=uid).delete()
        return JsonResponse({'status': 'ok'})


def postremove(request):
    uid = request.POST['uid']
    re = Post.objects.filter(id=uid).delete()
    return JsonResponse({'status': 'ok'})

def chat_send(request):
    FROM_id=request.POST['from_id']
    TOID_id=request.POST['to_id']
    msg=request.POST['message']

    from  datetime import datetime
    c=Messagechat()
    c.FROM_id=FROM_id
    c.TO_id=TOID_id
    c.message=msg
    c.date=datetime.now().date()
    c.time=datetime.now().time()
    c.save()
    return JsonResponse({'status':"ok"})

def chat_view_and(request):
    from_id=request.POST['from_id']
    to_id=request.POST['to_id']
    l=[]
    data1=Messagechat.objects.filter(FROM_id=from_id,TO_id=to_id).order_by('id')
    data2=Messagechat.objects.filter(FROM_id=to_id,TO_id=from_id).order_by('id')

    data= data1 | data2
    print(data)

    for res in data:
        l.append({'id':res.id,'from':res.FROM.id,'to':res.TO.id,'msg':res.message,'date':res.date})

    return JsonResponse({'status':"ok",'data':l})

def likes(request):
    lid=request.POST['lid']
    pid=request.POST['pid']
    obj=Like()
    if Like.objects.filter(USER__LOGIN_id=lid,POST_id=pid).exists():
        Like.objects.filter(USER__LOGIN_id=lid, POST_id=pid).delete()
        return JsonResponse({'status': "ok"})

    obj.USER=UserProfile.objects.get(LOGIN_id=lid)
    obj.POST_id=pid
    obj.date=datetime.datetime.now().date()
    obj.time=datetime.datetime.now().time()
    obj.save()

    return JsonResponse({'status':"ok"})


def user_viewcommentsreply(request):
    cid=request.POST['cid']
    res=Comments.objects.filter(COMMENT_id=cid)
    l=[]
    for i in res:
        l.append({'id':i.id,'userid':i.UserProfile.username,'userphoto':i.UserProfile.photo,'uploadpost':i.COMMENT.id , 'comment':i.reply,'date':i.date,'time':i.time})
    return JsonResponse({'status': 'ok','data':l})

def user_addcommentreply(request):
    lid = request.POST['lid']
    cid = request.POST['cid']

    reply=request.POST['reply']
    date=datetime.date.today()


    # obj=CommentReply()
    # obj.USERID=UserProfile.objects.get(LOGIN_id=lid)
    # obj.COMMENT_id=cid
    # obj.reply=reply
    # obj.date=date
    # obj.time=datetime.datetime.now().strftime('%H:%M:%S')
    # obj.save()

    return JsonResponse({'status': 'ok'})


###################ml




def user_viewnotification(request):
    lid= request.POST["lid"]
    res=Notifications.objects.filter(USER__LOGIN_id=lid,status='pending')
    l=[]

    for i in res:

        l.append({'id':i.id,'date':i.date,'post':i.POST.photo,'name':i.POST.USER.username,'image':i.POST.USER.photo})
    return JsonResponse({'status': 'ok','data':l})

################################## ACCEPT NOC
def accept_notification(request):
    nid= request.POST["nid"]
    Notifications.objects.filter(id=nid).update(status='approved')
    n=Notifications.objects.get(id=nid).POST.photo
    pid=Notifications.objects.get(id=nid).POST.id
    print(n)
    bottom=int(Notifications.objects.get(id=nid).bottom)
    left=int(Notifications.objects.get(id=nid).left)
    right=int(Notifications.objects.get(id=nid).right)
    top=int(Notifications.objects.get(id=nid).top)
    postimage=Notifications.objects.get(id=nid).POST.photo
    postimage=postimage.replace("/media/post/","")
    imagenews = Image.open("C:\\Users\\HP\\Downloads\\cyberbullyingdetection (2)\\cyberbullyingdetection\\media\\post\\" + postimage)
    width, height = imagenews.size
    new_image = Image.new("RGB", (width, height))
    def modify_pixel(pixel):
        return (pixel[0] ^ 124, pixel[1] ^ 178, pixel[2] ^ 167)
    for x in range(left, right):
        for y in range(top, bottom):
            pixel = imagenews.getpixel((x, y))
            new_pixel = modify_pixel(pixel)
            imagenews.putpixel((x, y), new_pixel)
    dates= datetime.datetime.now().strftime("%Y%m%d%H%M%f")+".bmp"
    p=Post.objects.get(id=pid)
    imagenews.save("C:\\Users\\HP\\Downloads\\cyberbullyingdetection (2)\\cyberbullyingdetection\\media\\post\\" + dates)
    p.photo="/media/post/"+ dates
    p.save()
    return JsonResponse({'status': 'ok'})

def reject_notification(request):
    nid= request.POST["nid"]
    Notifications.objects.filter(id=nid).update(status='reject')
    return JsonResponse({'status': 'ok'})


from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, precision_score, recall_score, \
    f1_score, RocCurveDisplay
import numpy as np

# def confusionmatrix(request):
#     # Load the dataset
#     import os
#     import time
#     import numpy as np
#     import pandas as pd
#     import re
#
#     import keras
#     from keras import layers, optimizers
#     from keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout
#     from keras.models import Model
#     from keras.preprocessing.text import Tokenizer
#     from keras.preprocessing.sequence import pad_sequences
#
#     from sklearn.model_selection import train_test_split
#     from sklearn.metrics import accuracy_score
#
#     import pickle
#     keras.backend.clear_session()
#     sms_df = pd.read_csv(r'C:\Users\afzal\PycharmProjects\cyberbullyingdetection\spamham.csv')
#
#     # Labels and messages
#     labels = sms_df.values[:, 1]
#     msgs = sms_df.values[:, 0]
#
#     # Split dataset
#     train_texts, test_texts, train_labels, test_labels = train_test_split(msgs, labels, test_size=0.1, random_state=500)
#
#     # Tokenization and padding
#     VOCABULARY_SIZE = 5000
#     tokenizer = Tokenizer(num_words=VOCABULARY_SIZE)
#     tokenizer.fit_on_texts(train_texts)
#     MAX_SENTENCE_LENGTH = 100
#     trainFeatures = tokenizer.texts_to_sequences(train_texts)
#     trainFeatures = pad_sequences(trainFeatures, MAX_SENTENCE_LENGTH, padding='post')
#     testFeatures = tokenizer.texts_to_sequences(test_texts)
#     testFeatures = pad_sequences(testFeatures, MAX_SENTENCE_LENGTH, padding='post')
#
#     # Define the model
#     model = Sequential()
#     model.add(Embedding(input_dim=VOCABULARY_SIZE + 1, output_dim=10, input_length=MAX_SENTENCE_LENGTH))
#     model.add(Conv1D(16, 5, activation='relu'))
#     model.add(Dropout(0.5))
#     model.add(GlobalMaxPooling1D())
#     model.add(Dropout(0.5))
#     model.add(Dense(8, activation='relu'))
#     model.add(Dense(1, activation='sigmoid'))
#
#     optimizer = optimizers.Adam(lr=0.001)
#     model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
#
#     # Train the model
#     model.fit(trainFeatures, train_labels, batch_size=32, epochs=20)
#
#     # Predict on test data
#     predictions = model.predict(testFeatures)
#     predicted_labels = [1 if p[0] > 0.6 else 0 for p in predictions]
#
#     # Confusion Matrix and Classification Report
#     cm = confusion_matrix(test_labels, predicted_labels)
#
#     cr = classification_report(test_labels, predicted_labels)
#
#     # Convert confusion matrix and classification report to string
#     cm_str = str(cm)
#     cr_str = str(cr)
#
#     # Pass the results to the template
#     context = {
#         'confusion_matrix': cm_str,
#         'classification_report': cr_str
#     }
#
#     return render(request, 'confusionmatrix.html', context)


#
# from django.shortcuts import render
# import numpy as np
# import pandas as pd
# import keras
# from keras.models import Sequential
# from keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout
# from keras.preprocessing.text import Tokenizer
# from keras.preprocessing.sequence import pad_sequences
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, precision_score, recall_score, \
#     f1_score
# import matplotlib.pyplot as plt
# import seaborn as sns
# import io
# import urllib, base64
#
#
# # Ensure that the necessary libraries are installed:
# # pip install matplotlib seaborn
#
# def confusionmatrix(request):
#     # --- Spam/Ham Dataset ---
#     # Load the SMS spam/ham dataset
#     sms_df = pd.read_csv(r'C:\Users\afzal\PycharmProjects\cyberbullyingdetection\spamham.csv')
#
#     # Labels and messages
#     labels = sms_df.values[:, 1]
#     msgs = sms_df.values[:, 0]
#
#     # Check for NaN or unexpected values in the dataset
#     if labels.isnull().any():
#         print("Warning: There are NaN values in the labels.")
#     if msgs.isnull().any():
#         print("Warning: There are NaN values in the messages.")
#
#     # Convert the labels to binary (0 and 1) if needed (ensure there are no unexpected values)
#     labels = labels.apply(lambda x: 1 if x == "spam" else 0)
#
#     # Split dataset for training and testing
#     train_texts, test_texts, train_labels, test_labels = train_test_split(msgs, labels, test_size=0.1, random_state=500)
#
#     # Tokenization and padding for text data
#     VOCABULARY_SIZE = 5000
#     tokenizer = Tokenizer(num_words=VOCABULARY_SIZE)
#     tokenizer.fit_on_texts(train_texts)
#     MAX_SENTENCE_LENGTH = 100
#     trainFeatures = tokenizer.texts_to_sequences(train_texts)
#     trainFeatures = pad_sequences(trainFeatures, MAX_SENTENCE_LENGTH, padding='post')
#     testFeatures = tokenizer.texts_to_sequences(test_texts)
#     testFeatures = pad_sequences(testFeatures, MAX_SENTENCE_LENGTH, padding='post')
#
#     # Define the deep learning model for Spam/Ham classification
#     model = Sequential()
#     model.add(Embedding(input_dim=VOCABULARY_SIZE + 1, output_dim=10, input_length=MAX_SENTENCE_LENGTH))
#     model.add(Conv1D(16, 5, activation='relu'))
#     model.add(Dropout(0.5))
#     model.add(GlobalMaxPooling1D())
#     model.add(Dropout(0.5))
#     model.add(Dense(8, activation='relu'))
#     model.add(Dense(1, activation='sigmoid'))
#
#     # Compile the model
#     optimizer = keras.optimizers.Adam(lr=0.001)
#     model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
#
#     # Train the model on the spam/ham dataset
#     model.fit(trainFeatures, train_labels, batch_size=32, epochs=20)
#
#     # Predict on test data
#     predictions = model.predict(testFeatures)
#     predicted_labels = [1 if p[0] > 0.6 else 0 for p in predictions]
#
#     # Ensure the predicted_labels are binary (0 or 1)
#     predicted_labels = np.array(predicted_labels)
#
#     # Confusion Matrix for Spam/Ham Dataset
#     cm_sms = confusion_matrix(test_labels, predicted_labels)
#
#     # Plot confusion matrix for Spam/Ham dataset
#     plt.figure(figsize=(6, 5))
#     sns.heatmap(cm_sms, annot=True, fmt='g', xticklabels=['Ham', 'Spam'], yticklabels=['Ham', 'Spam'])
#     plt.ylabel('Prediction', fontsize=13)
#     plt.xlabel('Actual', fontsize=13)
#     plt.title('Spam/Ham Confusion Matrix', fontsize=17)
#
#     # Save the plot to a BytesIO object and convert to base64 for embedding in HTML
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png')
#     buf.seek(0)
#     img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
#     buf.close()
#
#     # Metrics for Spam/Ham classification
#     accuracy_sms = accuracy_score(test_labels, predicted_labels)
#     precision_sms = precision_score(test_labels, predicted_labels)
#     recall_sms = recall_score(test_labels, predicted_labels)
#     f1_sms = f1_score(test_labels, predicted_labels)
#
#     print("\nSpam/Ham Classification Metrics:")
#     print(f"Accuracy: {accuracy_sms}")
#     print(f"Precision: {precision_sms}")
#     print(f"Recall: {recall_sms}")
#     print(f"F1-score: {f1_sms}")
#
#     # Classification report (use this for detailed metrics)
#     classification_rep = classification_report(test_labels, predicted_labels)
#
#     # Pass the results to the template
#     context = {
#         'confusion_matrix': str(cm_sms),
#         'classification_report': classification_rep,
#         'accuracy': accuracy_sms,
#         'precision': precision_sms,
#         'recall': recall_sms,
#         'f1_score': f1_sms,
#         'confusion_matrix_image': img_str  # Pass the image as base64
#     }
#
#     return render(request, 'confusionmatrix.html', context)


#
#
# def confusion_metrix(request):
#     import warnings
#     def warn(*args, **kwargs):
#         pass
#
#     warnings.warn = warn
#
#     import os
#     import time
#     import numpy as np
#     import pandas as pd
#     import re
#
#     import keras
#     from keras import layers, optimizers
#     from keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout
#     from keras.models import Model
#     from tensorflow.keras.preprocessing.text import Tokenizer
#     from keras.preprocessing.sequence import pad_sequences
#
#     from sklearn.model_selection import train_test_split
#     from sklearn.metrics import accuracy_score, confusion_matrix
#
#     import pickle
#     from keras.models import Sequential
#     import keras.backend as K
#
#     # Clear session to avoid memory issues
#     K.clear_session()
#
#     # Load data
#     sms_df = pd.read_csv(r'C:\kochi\Projects\cyberbullyingdetection\spamham.csv')
#
#     # Split data into labels and messages
#     labels = sms_df.values[:, 1]
#     msgs = sms_df.values[:, 0]
#
#     # Split dataset into train and test sets
#     train_texts, test_texts, train_labels, test_labels = train_test_split(msgs, labels, test_size=0.1, random_state=500)
#
#     # Prepare tokenizer for text processing
#     VOCABULARY_SIZE = 5000
#     tokenizer = Tokenizer(num_words=VOCABULARY_SIZE)
#     tokenizer.fit_on_texts(train_texts)
#
#     # Maximum sentence length (you can adjust this depending on your dataset)
#     MAX_SENTENCE_LENGTH = 100
#
#     # Tokenize and pad the sequences
#     trainFeatures = tokenizer.texts_to_sequences(train_texts)
#     trainFeatures = pad_sequences(trainFeatures, MAX_SENTENCE_LENGTH, padding='post')
#
#     testFeatures = tokenizer.texts_to_sequences(test_texts)
#     testFeatures = pad_sequences(testFeatures, MAX_SENTENCE_LENGTH, padding='post')
#
#     # Model parameters
#     FILTERS_SIZE = 16
#     KERNEL_SIZE = 5
#     EMBEDDINGS_DIM = 10
#     LEARNING_RATE = 0.001
#     BATCH_SIZE = 32
#     EPOCHS = 20
#
#     # Build the model
#     model = Sequential()
#     model.add(Embedding(input_dim=VOCABULARY_SIZE + 1, output_dim=EMBEDDINGS_DIM, input_length=MAX_SENTENCE_LENGTH))
#     model.add(Conv1D(FILTERS_SIZE, KERNEL_SIZE, activation='relu'))
#     model.add(Dropout(0.5))
#     model.add(GlobalMaxPooling1D())
#     model.add(Dropout(0.5))
#     model.add(Dense(8, activation='relu'))
#     model.add(Dense(1, activation='sigmoid'))
#
#     # Compile the model
#     optimizer = optimizers.Adam(lr=LEARNING_RATE)
#     model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
#
#     # Train the model
#     history = model.fit(trainFeatures, train_labels, batch_size=BATCH_SIZE, epochs=EPOCHS)
#
#     # Save the tokenizer and model weights
#     with open('tokenizer.pickle', 'wb') as handle:
#         pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
#
#     model_json = model.to_json()
#     with open("model.json", "w") as json_file:
#         json_file.write(model_json)
#     model.save_weights("model.h5")
#
#     # Predict on the test set
#     x = model.predict(testFeatures)
#     predicted = (x > 0.5).astype(int)  # Convert probabilities to binary labels (0 or 1)
#
#
#     print(len(test_labels),"jjjjjj")
#     print(len(predicted),"kkkkkk")
#
#     s=[]
#
#
#     for i in predicted:
#         a=i
#         # print(a[0],"helloiiiiiiii")
#
#         s.append(a[0])
#
#     print(s, "nnn")
#     print(test_labels, "mmmm")
#
#     print(type(s),type(test_labels),"hello")
#
#
#     k=[]
#
#     for i in test_labels:
#         k.append(i)
#
#     cm = confusion_matrix(k, s)
#
#     print(cm)
#     from  sklearn.metrics import  accuracy_score,f1_score, recall_score, precision_score,roc_curve
#     acc=accuracy_score(k,s)
#     f1score=f1_score(k,s)
#     rec=recall_score(k,s)
#     pre=precision_score(k,s)
#     import matplotlib.pyplot as plt
#     fpr, tpr, _ = roc_curve(k, s)
#
#     # Create the RocCurveDisplay object
#     roc_display = RocCurveDisplay(fpr=fpr, tpr=tpr).plot()
#
#     # Save the ROC curve as an image
#     plt.savefig(r'C:\kochi\Projects\cyberbullyingdetection\media\roc_curve.png')
#
#
#
#
#
#
#     return render(request,"cnfsn_mtrix.html",{'cf':cm, 'acc':acc, 'f1score': f1score,'rec':rec, 'pre': pre,  })
#
#

def confusion_metrix(request):
    import warnings
    warnings.filterwarnings("ignore")

    import os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import pickle

    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (
        accuracy_score, confusion_matrix, f1_score,
        recall_score, precision_score, roc_curve, RocCurveDisplay
    )

    import tensorflow.keras.backend as K
    from tensorflow.keras import optimizers
    from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.preprocessing.text import Tokenizer
    from tensorflow.keras.preprocessing.sequence import pad_sequences

    try:
        # Clear any previous Keras session
        K.clear_session()

        # === 1. Load and preprocess dataset ===
        csv_path = r'C:\kochi\Projects\cyberbullyingdetection\spamham.csv'

        # Check if file exists
        if not os.path.exists(csv_path):
            return render(request, "error.html", {
                'error_message': f"CSV file not found at: {csv_path}"
            })

        sms_df = pd.read_csv(csv_path)

        # Debug: Check initial data
        print(f"Initial dataset shape: {sms_df.shape}")
        print(f"Columns: {sms_df.columns.tolist()}")
        print(f"First few rows:")
        print(sms_df.head())

        # === FIX: SWAP THE COLUMNS ===
        # Your CSV has: Category=message_text, Message=labels
        # We need: message=message_text, label=labels
        sms_df = sms_df.rename(columns={'Category': 'message', 'Message': 'label'})

        # Check the swapped data
        print(f"After swapping columns:")
        print(f"Message column sample: {sms_df['message'].head(3).tolist()}")
        print(f"Label column sample: {sms_df['label'].head(10).tolist()}")
        print(f"Label types: {sms_df['label'].dtype}")
        print(f"Unique labels: {sms_df['label'].unique()}")

        # Convert labels to numeric (handle both string and numeric labels)
        if sms_df['label'].dtype == 'object':
            # Check if labels are string representations of numbers
            unique_labels = sms_df['label'].unique()
            print(f"String labels found: {unique_labels}")

            # Simple mapping - anything that can be converted to 0 or 1
            def convert_label(label):
                try:
                    # Try to convert to integer
                    label_int = int(float(str(label).strip()))
                    return 0 if label_int == 0 else 1
                except (ValueError, TypeError):
                    # If conversion fails, check for common patterns
                    label_str = str(label).lower().strip()
                    if label_str in ['ham', '0', 'non-spam', 'legitimate', 'safe']:
                        return 0
                    elif label_str in ['spam', '1', 'bullying', 'abusive']:
                        return 1
                    else:
                        return np.nan

            sms_df['label'] = sms_df['label'].apply(convert_label)
        else:
            # Already numeric, ensure binary (0/1)
            sms_df['label'] = pd.to_numeric(sms_df['label'], errors='coerce')
            sms_df['label'] = (sms_df['label'] > 0).astype(int)

        # Drop rows with NaN labels (unmapped values)
        initial_count = len(sms_df)
        sms_df = sms_df.dropna(subset=['label'])
        sms_df = sms_df.dropna(subset=['message'])
        final_count = len(sms_df)

        print(f"Rows dropped due to NaN: {initial_count - final_count}")
        print(f"Final dataset shape: {sms_df.shape}")
        print(f"Final label distribution:\n{sms_df['label'].value_counts()}")

        # Check if we have sufficient data
        if len(sms_df) < 10:
            return render(request, "error.html", {
                'error_message': f"Insufficient data after preprocessing. Only {len(sms_df)} rows remaining."
            })

        # Prepare inputs and labels
        labels = sms_df['label'].astype(np.int32).values
        messages = sms_df['message'].astype(str).values

        print(f"Sample messages: {messages[:3]}")
        print(f"Sample labels: {labels[:3]}")

        # === 2. Train/test split ===
        train_texts, test_texts, train_labels, test_labels = train_test_split(
            messages, labels, test_size=0.1, random_state=500, stratify=labels
        )

        print(f"Training samples: {len(train_texts)}")
        print(f"Testing samples: {len(test_texts)}")

        # === 3. Tokenization and padding ===
        VOCABULARY_SIZE = 5000
        MAX_SENTENCE_LENGTH = 100

        tokenizer = Tokenizer(num_words=VOCABULARY_SIZE)
        tokenizer.fit_on_texts(train_texts)

        train_sequences = tokenizer.texts_to_sequences(train_texts)
        test_sequences = tokenizer.texts_to_sequences(test_texts)

        train_features = pad_sequences(train_sequences, maxlen=MAX_SENTENCE_LENGTH, padding='post')
        test_features = pad_sequences(test_sequences, maxlen=MAX_SENTENCE_LENGTH, padding='post')

        # === 4. Build the model ===
        model = Sequential([
            Embedding(input_dim=VOCABULARY_SIZE + 1, output_dim=10, input_length=MAX_SENTENCE_LENGTH),
            Conv1D(16, 5, activation='relu'),
            Dropout(0.5),
            GlobalMaxPooling1D(),
            Dropout(0.5),
            Dense(8, activation='relu'),
            Dense(1, activation='sigmoid')
        ])

        optimizer = optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

        # === 5. Train the model ===
        history = model.fit(train_features, train_labels, batch_size=32, epochs=20, verbose=0)
        print(f"Training completed with final accuracy: {history.history['accuracy'][-1]:.4f}")

        # === 6. Save model and tokenizer ===
        with open('tokenizer.pickle', 'wb') as handle:
            pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

        model_json = model.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model_json)

        # FIX: Use the correct file extension for saving weights
        model.save_weights("model.weights.h5")

        # === 7. Predict on test set ===
        predictions = model.predict(test_features)
        predicted_labels = (predictions > 0.5).astype(int).flatten()

        # === 8. Evaluate ===
        cm = confusion_matrix(test_labels, predicted_labels)
        acc = accuracy_score(test_labels, predicted_labels)
        f1score = f1_score(test_labels, predicted_labels)
        rec = recall_score(test_labels, predicted_labels)
        pre = precision_score(test_labels, predicted_labels)
        fpr, tpr, _ = roc_curve(test_labels, predicted_labels)

        # === 9. Save ROC curve ===
        RocCurveDisplay(fpr=fpr, tpr=tpr).plot()
        roc_path = r'C:\kochi\Projects\cyberbullyingdetection\media\roc_curve.png'

        # Ensure directory exists
        os.makedirs(os.path.dirname(roc_path), exist_ok=True)
        plt.savefig(roc_path)
        plt.close()

        # === 10. Return to template ===
        return render(request, "cnfsn_mtrix.html", {
            'cf': cm.tolist(),  # Convert numpy array to list for template
            'acc': f"{acc:.4f}",
            'f1score': f"{f1score:.4f}",
            'rec': f"{rec:.4f}",
            'pre': f"{pre:.4f}",
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in confusion_metrix: {str(e)}")
        print(f"Detailed traceback: {error_details}")

        return render(request, "error.html", {
            'error_message': f"An error occurred: {str(e)}",
            'error_details': error_details
        })
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()


def default_view(request):
    # Redirect the user to the login page if they are not authenticated
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    # Redirect the user to the dashboard based on their role
    if request.user.role == request.user.Role.STUDENT:
        return redirect("dashboard:student")
    if request.user.role == request.user.Role.TEACHER:
        return redirect("dashboard:teacher")


def login_view(request):
    # Handle GET requests
    if request.method == "GET":
        return render(request, "login.html")

    # Handle POST requests
    if request.method == "POST":
        # Get the username and password from the POST request
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if the username and password are valid
        if not username or not password:
            messages.error(request, "Please enter a username and password")
            return redirect("accounts:login")

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if not user:
            messages.error(request, "Invalid username or password")
            return redirect("accounts:login")

        # Log in the user
        login(request, user)
        messages.success(request, "Logged in successfully")

        # Redirect the user based on their role
        if request.user.role == request.user.Role.STUDENT:
            return redirect("dashboard:student")
        if request.user.role == request.user.Role.TEACHER:
            return redirect("dashboard:teacher")


def signup_view(request):
    # Get student and teacher roles from the User model
    roles = [User.Role.choices[1], User.Role.choices[2]]

    # Handle GET requests
    if request.method == "GET":
        return render(
            request,
            "signup.html",
            {"roles": roles},
        )

    # Handle POST requests
    if request.method == "POST":
        # Get the input data from the POST request
        username = request.POST.get("username")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        role = request.POST.get("role")

        # Create a dictionary of the input data
        input = {
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "role": role,
        }

        # Check if all fields are filled
        if (
            not username
            or not password
            or not first_name
            or not last_name
            or not email
            or not role
        ):
            messages.error(request, "Please fill in all fields")
            return redirect("accounts:signup")

        # Check if username or email already exists
        validation_error = {}

        if User.objects.filter(username=username).exists():
            validation_error["username"] = "Account with this username already exists"
        if User.objects.filter(email=email).exists():
            validation_error["email"] = "Account with this email already exists"

        if validation_error:
            return render(
                request,
                "signup.html",
                {
                    "input": input,
                    "roles": roles,
                    "validation_error": validation_error,
                },
            )

        # Create a new user
        User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        messages.success(request, "Account created successfully")

        # Redirect the user to the login page
        return redirect("accounts:login")


@login_required
def logout_view(request):
    # Log out the user
    logout(request)
    messages.success(request, "Logged out successfully")

    # Redirect the user to the login page
    return redirect("accounts:login")


@login_required
def profile_view(request):
    # Render the profile page
    return render(request, "profile.html", {"user": request.user})


@login_required
def change_profile_picture_view(request):
    # Check if an image file is uploaded
    if not request.FILES.get("profile_picture"):
        messages.error(request, "No image file selected")
        return redirect("accounts:profile")

    # Handle the image upload
    image = request.FILES["profile_picture"]

    # Validate file type
    if not image.content_type.startswith("image/"):
        messages.error(request, "Please upload an image file.")
        return redirect("accounts:profile")

    # Delete old profile picture if it exists
    if request.user.profile_picture:
        request.user.profile_picture.delete()

    # Save the image
    request.user.profile_picture = image
    request.user.save()
    messages.success(request, "Profile picture updated successfully")

    # Redirect the user to the profile page with the updated profile picture
    return redirect("accounts:profile")


@login_required
def change_profile_information_view(request):
    # Get the input data from the POST request
    username = request.POST.get("username")
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    email = request.POST.get("email")
    biography = request.POST.get("biography")

    # Check if username or email already exists
    validation_error = {}

    if (
        username != request.user.username
        and User.objects.filter(username=username).exists()
    ):
        validation_error["username"] = "Account with this username already exists"
    if email != request.user.email and User.objects.filter(email=email).exists():
        validation_error["email"] = "Account with this email already exists"

    if validation_error:
        return render(
            request,
            "profile.html",
            {
                "user": request.user,
                "input": {"username": username, "email": email},
                "validation_error": validation_error,
            },
        )

    # Update the user's information
    request.user.username = username
    request.user.first_name = first_name
    request.user.last_name = last_name
    request.user.email = email
    request.user.biography = biography
    request.user.save()
    messages.success(request, "Profile updated successfully")

    # Redirect the user to the profile page with the updated information
    return redirect("accounts:profile")


@login_required
def change_profile_password_view(request):
    # Get the input data from the POST request
    current_password = request.POST.get("current_password")
    new_password = request.POST.get("new_password")
    confirm_password = request.POST.get("confirm_password")

    # Check if all fields are filled
    if not current_password or not new_password or not confirm_password:
        messages.error(
            request,
            "Please enter a current password, new password, and confirm new password",
        )
        return redirect("accounts:profile")

    # Check if the current password is correct
    if not request.user.check_password(current_password):
        return render(
            request,
            "profile.html",
            {"validation_error": {"current_password": "Current password is incorrect"}},
        )

    # Check if the new password and confirm password match
    if new_password != confirm_password:
        return render(
            request,
            "profile.html",
            {"validation_error": {"confirm_password": "Passwords do not match"}},
        )

    # Update the user's password
    request.user.set_password(new_password)
    request.user.save()

    # Log in the user
    login(request, request.user)
    messages.success(request, "Password updated successfully")

    # Redirect the user to the profile page
    return redirect("accounts:profile")

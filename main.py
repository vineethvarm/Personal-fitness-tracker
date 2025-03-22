import pyrebase
import requests
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window

firebaseConfig = {
    "apiKey": "AIzaSyCTdEE8u_waeglHCAe--L-XuZWmfyi33uc",
    "authDomain": "fitnesstracker-20003.firebaseapp.com",
    "databaseURL": "https://fitnesstracker-20003.firebaseio.com/",
    "projectId": "fitnesstracker-20003",
    "storageBucket": "fitnesstracker-20003.firebasestorage.app",
    "messagingSenderId": "154505403780",
    "appId": "1:154505403780:web:8fd7e15f588255ae8d51d1",
    "measurementId": "G-YRBBKKHDSV"
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

class LoginScreen(MDScreen):
    def login_user(self, email, password):
        try:
            if not email or not password:
                self.ids.error_label.text = "Email and password cannot be empty."
                return
            
            user = auth.sign_in_with_email_and_password(email, password)
            self.manager.current = "dashboard"  # Switch to dashboard screen

        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 400:
                error_message = e.response.json().get("error", {}).get("message", "Invalid email or password.")
            else:
                error_message = "No response from server"
            self.ids.error_label.text = f"Login Failed: {error_message}"
        except Exception as e:
            self.ids.error_label.text = f"An error occurred: {str(e)}"

    def go_to_signup(self):
        self.manager.current = "signup"  # Switch to signup screen

class SignupScreen(MDScreen):
    def signup_user(self, email, password, name):
        try:
            user = auth.create_user_with_email_and_password(email, password)  # Use the email & password fields

            user_id = user['localId']
            data = {"name": name}
            db.child("users").child(user_id).set(data)  # Save user name to Firebase database
            print(f"Saving user data for ID: {user_id}")  # Log saving user data
            print(f"Saving user data for ID: {user_id}")  # Log saving user data
            print(f"Saving user data for ID: {user_id}")  # Log saving user data
            print(f"Saving user data for ID: {user_id}")  # Log saving user data
            print(f"Saving user data for ID: {user_id}")  # Log saving user data
            self.manager.current = "login"  # Switch to login screen after successful signup





        except Exception as e:
            self.ids.error_label.text = f"Signup Failed: {e}"

class DashboardScreen(MDScreen):
    def on_enter(self):
        user = auth.current_user
        if user:
            user_id = user['localId']
            user_data = db.child("users").child(user_id).get()
            if user_data.val():
                self.ids.welcome_label.text = f"Welcome, {user_data.val().get('name', 'User')}!"

    def go_to_fitness_tracker(self):
        self.manager.current = "fitness_tracker"

    def on_logout(self):
        auth.current_user = None
        self.manager.current = "login"

class FitnessTrackerScreen(MDScreen):
    def log_activity(self, activity, duration, calories):
        user = auth.current_user
        if user:
            user_id = user['localId']
            data = {"activity": activity, "duration": duration, "calories": calories}
            db.child("users").child(user_id).child("activities").push(data)
            self.manager.current = "dashboard"  # Return to dashboard after logging activity

class PersonalFitnessApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        Builder.load_file("fitness_tracker.kv")  # Load the .kv file

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(FitnessTrackerScreen(name="fitness_tracker"))
        Window.size = (400, 600)  # Set window size to something reasonable


        return sm

if __name__ == "__main__":
    PersonalFitnessApp().run()

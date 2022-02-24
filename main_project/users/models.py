from django.db import models


class City(models.Model):
    name = models.CharField(max_length=50)


class MyUser(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    other_name = models.CharField(max_length=30)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # considering this as login
    phone = models.CharField(max_length=14)
    birthday = models.DateField(null=True)
    is_admin = models.BooleanField(default=False)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)
    additional_info = models.CharField(max_length=300)

    def check_password(self, password):
        return self.password == password

    def get_short_user_model(self):
        data = {
            'id': self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
        }
        return data

    def get_current_user_response_model(self):
        data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "other_name": self.other_name,
            "email": self.email,
            "phone": self.phone,
            "birthday": self.birthday,
            "is_admin": self.is_admin
        }

        return data

    def get_privateDetailUserResponseModel(self):
        data = {
            'id': self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "other_name": self.other_name,
            "email": self.email,
            "phone": self.phone,
            "birthday": self.birthday,
            "is_admin": self.is_admin,
            "city": self.city,
            "additional_info": self.additional_info,
        }
        return data

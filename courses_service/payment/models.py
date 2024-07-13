from django.db import models
from courses.models import Course


class Order(models.Model):
    user = models.EmailField()
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='orders')
    price = models.DecimalField(max_digits=10,
                                decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=True)

    def __str__(self):
        return f'Order {self.id}'
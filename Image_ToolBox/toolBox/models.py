from django.db import models

# User Model
from django.contrib.auth.models import User

# Time Zone
from django.utils import timezone


class Projects(models.Model):
	Project_Name = models.CharField(max_length = 100)
	Lastupdate = models.DateField(default=timezone.now)
	Progress = models.PositiveIntegerField(default = 0)
	Total_effects = models.PositiveIntegerField(default = 0)
	status = models.CharField(max_length= 100, choices=[('0','Complete'),('1','Not start'),('2','Pending'),('3','Working on')], default=('1','Not start'))
	User = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.Project_Name)


class ProjectsImages(models.Model):
	Project = models.ForeignKey(Projects, on_delete = models.CASCADE)
	Image = models.ImageField(upload_to='Projects/', default='Projects/p.png')
	current_image_width = models.PositiveIntegerField(default=0)
	current_image_height = models.PositiveIntegerField(default=0)
	current_image_format = models.PositiveIntegerField(default=0)
	current_image_Min_intensity = models.PositiveIntegerField(default=0)
	current_image_Max_intensity = models.PositiveIntegerField(default=0)

	def __str__(self):
		return str(self.Project.Project_Name)



class BlendingWithCurrentImage(models.Model):
	current_image = models.ForeignKey(ProjectsImages, on_delete=models.CASCADE)
	blending_image = models.ImageField(upload_to='Blending_images/', default='Blending_images/p.png')

	def __str__(self):
		return str(self.current_image.Project.Project_Name)


class ZoomedImages(models.Model):
	width = models.PositiveBigIntegerField(default=0)
	height = models.PositiveBigIntegerField(default=0)
	x_position = models.PositiveBigIntegerField(default=0)
	y_position = models.PositiveBigIntegerField(default=0)
	image_format = models.PositiveIntegerField(default=0)
	zoomed_image = models.ImageField(upload_to='zoomedImages/', default='zoomedImages/p.png')
	target_image = models.ForeignKey(ProjectsImages, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.target_image.Project.Project_Name)

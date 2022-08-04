from django.forms import ModelForm
from .models import *


# Project form
class ProjectForm(ModelForm):

    class Meta:
        model = Projects
        fields = ["Project_Name"]


# Update Project form
class UpdateProjectForm(ModelForm):

    class Meta:
        model = Projects
        fields = ["Project_Name", "Progress", "status"]

# Images Form
class ProjectImageForm(ModelForm):

    class Meta:
        model = ProjectsImages
        fields = ['Image']
    
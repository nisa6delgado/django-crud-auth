from import_export import resources, fields
from .models import Task

class TaskResource(resources.ModelResource):
    title = fields.Field(column_name='Título', attribute='title')
    description = fields.Field(column_name='Descripción', attribute='description')
    created = fields.Field(column_name='Fecha de creación', attribute='created')
    completed = fields.Field(column_name='Está completado?', attribute='completed')
    important = fields.Field(column_name='Es importante?', attribute='important')
    user = fields.Field(column_name='Usuario', attribute='user')

    
    def dehydrate_created(self, Task):
        return Task.created.strftime('%d/%m/%Y')


    def dehydrate_completed(self, Task):
        if (Task.completed):
            return 'Si'
        else:
            return 'No'
        

    def dehydrate_important(self, Task):
        if (Task.important):
            return 'Si'
        else:
            return 'No'


    class Meta:
        model = Task

        fields = (
            'title',
            'description',
            'created',
            'completed',
            'important',
            'user',
        )

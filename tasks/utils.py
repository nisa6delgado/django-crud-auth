from import_export.formats.base_formats import XLSX
from .resources import TaskResource

def importFromExcel(filePath):
    taskResource = TaskResource()
    
    with open(filePath, 'rb') as file:
        excelFormat = XLSX()

        dataset = excelFormat.create_dataset(file.read())
        
        result = taskResource.import_data(dataset, dry_run=False)
        
        if result.has_errors():
            for error in result.base_errors:
                print(f"  - {error}")

            for row_errors in result.row_errors():
                print(f"  - Fila {row_errors[0]}: {row_errors[1]}")
        
        return True, 'Éxito'